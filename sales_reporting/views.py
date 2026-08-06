from collections import defaultdict
from datetime import date

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.shortcuts import render

from .forms import (
    SalesReportUploadForm,
    WorkbookInspectorForm,
)
from .models import Category, CategoryResult
from .services.importer import (
    SalesImportError,
    import_sales_workbook,
)
from .services.workbook_reader import (
    WorkbookReadError,
    read_workbook_metadata,
)
from .services.worksheet_explorer import (
    WorksheetExplorerError,
    inspect_worksheet,
)


@login_required

def upload_sales_reports(request):
    import_results = []
    if request.method == "POST":
        form = SalesReportUploadForm(
            request.POST,
            request.FILES,
        )
        if form.is_valid():
            uploaded_files = form.cleaned_data["files"]
            replace_existing = (
                request.POST.get("replace_existing") == "on"
            )
            for uploaded_file in uploaded_files:
                try:
                    summary = import_sales_workbook(
                        uploaded_file,
                        replace_existing=replace_existing,
                    )
                    import_results.append(
                        {
                            "success": True,
                            "filename": summary.source_filename,
                            "store_number": summary.store_number,
                            "reporting_month": summary.reporting_month,
                            "category_results_created": (
                                summary.category_results_created
                            ),
                            "categories_created": (
                                summary.categories_created
                            ),
                            "categories_updated": (
                                summary.categories_updated
                            ),
                            "replaced_existing_import": (
                                summary.replaced_existing_import
                            ),
                        }
                    )

                except SalesImportError as exc:
                    import_results.append(
                        {
                            "success": False,
                            "filename": uploaded_file.name,
                            "error": str(exc),
                        }
                    )
            successful_count = sum(
                1 for result in import_results
                if result["success"]
            )
            failed_count = (
                len(import_results) - successful_count
            )
            if successful_count:
                messages.success(
                    request,
                    (
                        f"Imported {successful_count} workbook(s) "
                        "successfully."
                    ),
                )
            if failed_count:
                messages.error(
                    request,
                    (
                        f"{failed_count} workbook(s) failed or "
                        "were skipped."
                    ),
                )
    else:
        form = SalesReportUploadForm()
    return render(
        request,
        "sales_reporting/upload.html",
        {
            "form": form,
            "import_results": import_results,
        },
    )

@login_required
def developer_workbook_inspector(request):
    metadata = None
    inspection = None

    if request.method == "POST":
        form = WorkbookInspectorForm(
            request.POST,
            request.FILES,
        )

        if form.is_valid():
            uploaded_file = form.cleaned_data["workbook"]

            try:
                metadata = read_workbook_metadata(uploaded_file)
                inspection = inspect_worksheet(uploaded_file)

                messages.success(
                    request,
                    "Workbook inspected successfully.",
                )

            except (
                WorkbookReadError,
                WorksheetExplorerError,
            ) as exc:
                messages.error(request, str(exc))
    else:
        form = WorkbookInspectorForm()

    return render(
        request,
        "sales_reporting/developer_inspector.html",
        {
            "form": form,
            "metadata": metadata,
            "inspection": inspection,
        },
    )

@login_required
def developer_category_import(request):
    import_result = None

    if request.method == "POST":
        form = WorkbookInspectorForm(
            request.POST,
            request.FILES,
        )

        if form.is_valid():
            uploaded_file = form.cleaned_data["workbook"]

            replace_existing = (
                request.POST.get("replace_existing") == "on"
            )

            try:
                import_result = import_sales_workbook(
                    uploaded_file,
                    replace_existing=replace_existing,
                )

                messages.success(
                    request,
                    (
                        f"Imported "
                        f"{import_result.category_results_created} "
                        f"category results for store "
                        f"{import_result.store_number}."
                    ),
                )

            except SalesImportError as exc:
                messages.error(request, str(exc))
    else:
        form = WorkbookInspectorForm()

    return render(
        request,
        "sales_reporting/developer_category_import.html",
        {
            "form": form,
            "import_result": import_result,
        },
    )

@login_required
def category_trend(request):
    selected_to_month = request.GET.get("to_month", "12")

    try:
        selected_to_month = int(selected_to_month)
    except (TypeError, ValueError):
        selected_to_month = 12

    selected_to_month = max(1, min(selected_to_month, 12))

    current_year = date.today().year

    selected_category_code = request.GET.get(
        "category",
        "2320",
    )
    selected_year = request.GET.get(
        "year",
        str(current_year),
    )
    selected_metric = request.GET.get(
        "metric",
        "quantity",
    )

    allowed_metrics = {
        "quantity": "Units",
        "sales": "Sales",
        "gross_margin": "Gross Margin",
    }

    if selected_metric not in allowed_metrics:
        selected_metric = "quantity"

    try:
        selected_year = int(selected_year)
    except (TypeError, ValueError):
        selected_year = current_year

    # Keep the main dropdown focused on the primary categories.
    categories = Category.objects.filter(
        level=2,
    ).order_by("name")

    # Unlike the dropdown, the selected category can be at any level.
    selected_category = (
        Category.objects
        .select_related("parent")
        .filter(code=selected_category_code)
        .first()
    )

    available_years = list(
        CategoryResult.objects
        .values_list(
            "sales_import__reporting_month__year",
            flat=True,
        )
        .distinct()
        .order_by(
            "-sales_import__reporting_month__year"
        )
    )

    results = CategoryResult.objects.none()

    if selected_category:
        results = (
            CategoryResult.objects
            .filter(
                category=selected_category,
                sales_import__reporting_month__year=selected_year,
                sales_import__reporting_month__month__lte=selected_to_month,
            )
            .select_related(
                "sales_import",
                "sales_import__store",
                "category",
            )
            .order_by(
                "sales_import__store__number",
                "sales_import__reporting_month",
            )
        )

    all_month_labels = [
        "Jan",
        "Feb",
        "Mar",
        "Apr",
        "May",
        "Jun",
        "Jul",
        "Aug",
        "Sep",
        "Oct",
        "Nov",
        "Dec",
    ]

    month_labels = all_month_labels

    month_options = list(
        enumerate(all_month_labels, start=1)
    )

    store_month_values = defaultdict(
        lambda: {
            month_number: None
            for month_number in range(1, 13)
        }
    )

    for result in results:
        store_number = result.sales_import.store.number
        month_number = (
            result.sales_import.reporting_month.month
        )

        value = getattr(result, selected_metric)

        store_month_values[store_number][
            month_number
        ] = float(value)

    table_rows = []

    for store_number in sorted(store_month_values):
        monthly_values = store_month_values[
            store_number
        ]

        values = [
            monthly_values[month_number]
            for month_number in range(1, 13)
        ]

        non_null_values = [
            value
            for value in values
            if value is not None
        ]

        total = (
            sum(non_null_values)
            if non_null_values
            else 0
        )

        table_rows.append(
            {
                "store_number": store_number,
                "values": values,
                "total": total,
            }
        )

    chart_datasets = []

    for row in table_rows:
        chart_datasets.append(
            {
                "label": (
                    f"Store {row['store_number']}"
                ),
                "data": row["values"],
                "fill": False,
                "tension": 0.2,
            }
        )

    # --------------------------------------------------
    # Drill-down categories
    # --------------------------------------------------

    child_categories = []

    if selected_category:
        raw_children = list(
            selected_category.children
            .all()
            .order_by("name", "code")
        )

        # Some D365 categories have one child with the
        # exact same description and identical results.
        #
        # Example:
        # 30230 - BEER 6PK CANS
        # 40450 - BEER 6PK CANS
        #
        # That child adds no useful drill-down information,
        # so do not display it as another navigation level.
        if len(raw_children) == 1:
            only_child = raw_children[0]

            parent_name = (
                selected_category.name
                .strip()
                .casefold()
            )
            child_name = (
                only_child.name
                .strip()
                .casefold()
            )

            if parent_name == child_name:
                raw_children = []

        child_category_ids = [
            child.id
            for child in raw_children
        ]

        child_totals = {}

        if child_category_ids:
            total_rows = (
                CategoryResult.objects
                .filter(
                    category_id__in=child_category_ids,
                    sales_import__reporting_month__year=selected_year,
                    sales_import__reporting_month__month__lte=selected_to_month,
                )
                .values("category_id")
                .annotate(
                    total=Sum(selected_metric)
                )
            )

            child_totals = {
                row["category_id"]: (
                    float(row["total"])
                    if row["total"] is not None
                    else 0
                )
                for row in total_rows
            }

        for child in raw_children:
            child_categories.append(
                {
                    "category": child,
                    "total": child_totals.get(
                        child.id,
                        0,
                    ),
                }
            )

        # --------------------------------------------------
    # Store opportunity analysis
    # --------------------------------------------------

    opportunity_rows = []
    chain_share = 0
    chain_share_percentage = 0
    total_opportunity = 0
    opportunity_parent = None

    # Show opportunity analysis when there is no further
    # meaningful category drill-down.
    if (
        selected_category
        and selected_category.parent
        and not child_categories
    ):
        opportunity_parent = selected_category.parent

        common_filters = {
            "sales_import__reporting_month__year": (
                selected_year
            ),
            "sales_import__reporting_month__month__lte": (
                selected_to_month
            ),
        }

        selected_store_totals = (
            CategoryResult.objects
            .filter(
                category=selected_category,
                **common_filters,
            )
            .values(
                "sales_import__store__number",
            )
            .annotate(
                total=Sum(selected_metric),
            )
        )

        parent_store_totals = (
            CategoryResult.objects
            .filter(
                category=opportunity_parent,
                **common_filters,
            )
            .values(
                "sales_import__store__number",
            )
            .annotate(
                total=Sum(selected_metric),
            )
        )

        selected_by_store = {
            row["sales_import__store__number"]: float(
                row["total"] or 0
            )
            for row in selected_store_totals
        }

        parent_by_store = {
            row["sales_import__store__number"]: float(
                row["total"] or 0
            )
            for row in parent_store_totals
        }

        chain_selected_total = sum(
            selected_by_store.values()
        )
        chain_parent_total = sum(
            parent_by_store.values()
        )

        if chain_parent_total:
            chain_share = (
                chain_selected_total
                / chain_parent_total
            )

        chain_share_percentage = chain_share * 100

        for store_number, parent_total in (
            parent_by_store.items()
        ):
            actual = selected_by_store.get(
                store_number,
                0,
            )

            store_share = None

            if parent_total:
                store_share = actual / parent_total

            expected = parent_total * chain_share

            opportunity = max(
                expected - actual,
                0,
            )

            variance = actual - expected

            if store_share is None:
                status = "No parent data"
            elif chain_share == 0:
                status = "No benchmark"
            elif store_share >= chain_share * 1.05:
                status = "Strong"
            elif store_share >= chain_share * 0.95:
                status = "On benchmark"
            else:
                status = "Opportunity"

            opportunity_rows.append(
                {
                    "store_number": store_number,
                    "actual": actual,
                    "parent_total": parent_total,
                    "store_share": store_share,
                    "store_share_percentage": (
                        store_share * 100
                        if store_share is not None
                        else None
                    ),
                    "expected": expected,
                    "variance": variance,
                    "opportunity": opportunity,
                    "status": status,
                }
            )

        opportunity_rows.sort(
            key=lambda row: (
                row["opportunity"],
                row["actual"],
            ),
            reverse=True,
        )

        total_opportunity = sum(
            row["opportunity"]
            for row in opportunity_rows
        )



    # --------------------------------------------------
    # Breadcrumbs
    # --------------------------------------------------

    breadcrumbs = []

    if selected_category:
        current_node = selected_category

        while current_node:
            # Do not include division-level nodes such as
            # 130 - Convenience Store in this breadcrumb.
            if current_node.level >= 2:
                breadcrumbs.append(current_node)

            current_node = current_node.parent

        breadcrumbs.reverse()

    return render(
        request,
        "sales_reporting/category_trend.html",
        {
            "categories": categories,
            "selected_category": selected_category,
            "selected_category_code": (
                selected_category_code
            ),
            "selected_year": selected_year,
            "selected_metric": selected_metric,
            "selected_metric_label": (
                allowed_metrics[selected_metric]
            ),
            "metric_options": allowed_metrics,
            "available_years": available_years,

            "month_labels": month_labels,
            "month_options": month_options,
            "selected_to_month": selected_to_month,

            "table_rows": table_rows,
            "chart_datasets": chart_datasets,

            "child_categories": child_categories,
            "breadcrumbs": breadcrumbs,

            "opportunity_rows": opportunity_rows,
            "opportunity_parent": opportunity_parent,
            "chain_share": chain_share,
            "chain_share_percentage": chain_share_percentage,
            "total_opportunity": total_opportunity,
        },
    )