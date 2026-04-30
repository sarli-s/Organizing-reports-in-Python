# import sys
# import os

# sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
# from Entities.attendance import AttendanceRow, AttendanceReport
# from strategies.strategy_base import BaseTransformationStrategy, TransformationError


# class TransformationService:
#     """
#     Applies a transformation strategy to every row in an AttendanceReport.
#     The service is unaware of the concrete strategy it receives - it may be
#     a raw strategy or a ValidatingStrategyDecorator. If transformation of a
#     single row fails validation, the service falls back to the original row.
#     """

#     def __init__(self, strategy_registry: dict[str, BaseTransformationStrategy]):
#         self._registry = strategy_registry

#     def transform(self, report: AttendanceReport) -> AttendanceReport:
#         strategy = self._registry.get(report.report_type)
#         if not strategy:
#             raise ValueError(f"No strategy registered for report type: {report.report_type}")

#         transformed_rows = []
#         for row in report.rows:
#             try:
#                 transformed_rows.append(strategy.transform_row(row))
#             except TransformationError as e:
#                 print(f"[TransformationService] Validation failed, keeping original row: {e}")
#                 transformed_rows.append(row)

#         return AttendanceReport(
#             employee_name=report.employee_name,
#             month=report.month,
#             year=report.year,
#             report_type=report.report_type,
#             rows=tuple(transformed_rows),
#             total_days=report.total_days,
#             total_hours_100=report.total_hours_100,
#             total_hours_125=report.total_hours_125,
#             total_hours_150=report.total_hours_150,
#             total_hours_shabbat=report.total_hours_shabbat,
#             hourly_rate=report.hourly_rate,
#             total_payment=report.total_payment,
#         )

import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from Entities.attendance import AttendanceRow, AttendanceReport
from strategies.strategy_base import BaseTransformationStrategy, TransformationError


class TransformationService:
    """
    Applies a transformation strategy to every row in an AttendanceReport,
    then enriches the report with missing data and calculated totals.
    The service is unaware of whether the strategy is raw or decorated.
    """

    def __init__(self, strategy_registry: dict[str, BaseTransformationStrategy]):
        self._registry = strategy_registry

    def transform(self, report: AttendanceReport) -> AttendanceReport:
        strategy = self._registry.get(report.report_type)
        if not strategy:
            raise ValueError(f"No strategy registered for report type: {report.report_type}")

        transformed_rows = []
        for row in report.rows:
            try:
                transformed_rows.append(strategy.transform_row(row))
            except TransformationError as e:
                print(f"[TransformationService] Validation failed, keeping original row: {e}")
                transformed_rows.append(row)

        transformed_report = AttendanceReport(
            employee_name=report.employee_name,
            month=report.month,
            year=report.year,
            report_type=report.report_type,
            rows=tuple(transformed_rows),
        )

        # Enrich with missing data and calculated totals
        inner_strategy = strategy._inner if hasattr(strategy, '_inner') else strategy
        return inner_strategy.enrich_report(transformed_report)