from pyfcm import FCMNotification
import logging

logger = logging.getLogger(__name__)

class NotificationService:
    def __init__(self, project_id: str, service_account_file: str = None):
        # Инициализация FCM с project_id и путем к файлу учетных данных сервисного аккаунта
        self.push_service = FCMNotification(project_id=project_id, service_account_file=service_account_file)

    async def send_notification(
        self,
        fcm_tokens: list[str],
        title: str,
        message: str,
        data: dict = None
    ) -> None:
        if not fcm_tokens:
            return

        try:
            response = self.push_service.notify(
                fcm_token=fcm_tokens,
                notification_title=title,
                notification_body=message,
                data_message=data
            )
            logger.info(f"FCM Response: {response}")
        except Exception as e:
            logger.error(f"FCM Error: {str(e)}")
