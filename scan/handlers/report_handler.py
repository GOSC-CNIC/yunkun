from django.http import FileResponse
from api.viewsets import CustomGenericViewSet
from core import errors
from scan.managers import TaskManager, VtReport
from django.utils.translation import gettext_lazy as _
from scan.models import VtTask
from io import BytesIO


class ReportHandler:
    @staticmethod
    def download_task_report(view: CustomGenericViewSet, request, kwargs):
        """
        下载安全扫描任务报告
        """
        try:
            task_id = kwargs.get("task_id", None)
            task = TaskManager.get_task_by_id(task_id=task_id, user_id=request.user.id)
            if task is None:
                raise errors.BadRequest(message=_("任务ID无效"), code="InvalidTaskID")
            if task.task_status != VtTask.Status.DONE:
                raise errors.BadRequest(message=_("任务未完成"), code="ScanTaskNotDone")
            if task.report.type == VtReport.FileType.HTML:
                html_bytes = task.report.content
                response = FileResponse(
                    BytesIO(html_bytes),
                    as_attachment=True,
                    filename=task.report.filename,
                )
                response["Content-Type"] = "application/octet-stream"
                return response
            if task.report.type == VtReport.FileType.PDF:
                pdf_bytes = task.report.content
                response = FileResponse(
                    BytesIO(pdf_bytes),
                    as_attachment=True,
                    filename=task.report.filename,
                )
                response["Content-Type"] = "application/octet-stream"
                return response
        except Exception as exc:
            return view.exception_response(exc)
