from typing import List, Optional, Union
from datetime import datetime
from ...domain.entities.reminder import ReminderEntity
from ...infrastructure.repositories.reminder_repository import ReminderRepository

class ReminderUseCases:
    def __init__(self, reminder_repository: ReminderRepository):
        self.reminder_repository = reminder_repository

    # ... (create_reminder, get_user_reminders, get_today_reminders, delete_reminder are unchanged) ...
    async def create_reminder(self, user_id: str, title: str, time: str, frequency: str, frequency_details: Optional[Union[List[int], int]] = None) -> str:
        reminder = ReminderEntity(
            user_id=user_id,
            title=title,
            time=time,
            frequency=frequency,
            frequency_details=frequency_details
        )
        return await self.reminder_repository.create(reminder)

    async def get_user_reminders(self, user_id: str) -> List[dict]:
        reminders = await self.reminder_repository.find_by_user(user_id)
        return [self._format_reminder(r) for r in reminders]

    async def get_today_reminders(self, user_id: str) -> List[dict]:
        all_reminders = await self.reminder_repository.find_by_user(user_id)
        today = datetime.utcnow().date()
        today_weekday = today.weekday() # Monday is 0 and Sunday is 6

        today_reminders = []
        for r in all_reminders:
            is_today = False
            if r.frequency == 'daily':
                is_today = True
            elif r.frequency == 'weekly' and isinstance(r.frequency_details, list):
                if today_weekday in r.frequency_details:
                    is_today = True
            elif r.frequency == 'monthly' and isinstance(r.frequency_details, int):
                if today.day == r.frequency_details:
                    # Adicionar lógica para lidar com meses que não têm o dia (ex: dia 31 em Fev) - opcional
                    is_today = True

            if is_today:
                reminder_dict = self._format_reminder(r)
                # Check completion based on date part only
                reminder_dict['completed'] = r.last_completed_date.date() == today if r.last_completed_date else False
                today_reminders.append(reminder_dict)

        # Ordenar pelo horário
        today_reminders.sort(key=lambda x: datetime.strptime(x['time'], '%H:%M').time())

        return today_reminders

    async def delete_reminder(self, reminder_id: str, user_id: str) -> bool:
        reminder = await self.reminder_repository.find_by_id(reminder_id)
        if not reminder or reminder.user_id != user_id:
            raise ValueError("Reminder not found or unauthorized")
        return await self.reminder_repository.delete(reminder_id)


    async def toggle_today_completion(self, reminder_id: str, user_id: str) -> bool:
        reminder = await self.reminder_repository.find_by_id(reminder_id)
        if not reminder or reminder.user_id != user_id:
            raise ValueError("Reminder not found or unauthorized")

        today = datetime.utcnow().date()
        update_data = {}
        if reminder.last_completed_date and reminder.last_completed_date.date() == today:
            # Mark as not completed by setting the date to None
            update_data["last_completed_date"] = None
        else:
            # Mark as completed by setting the date to now
            update_data["last_completed_date"] = datetime.utcnow()

        # Pass only the update data dictionary to the repository
        return await self.reminder_repository.update(reminder_id, update_data)

    async def update_reminder(self, reminder_id: str, user_id: str, title: str, time: str, frequency: str, frequency_details: Optional[Union[List[int], int]] = None) -> bool:
        reminder = await self.reminder_repository.find_by_id(reminder_id)
        if not reminder or reminder.user_id != user_id:
            raise ValueError("Reminder not found or unauthorized")

        update_data = {
            "title": title,
            "time": time,
            "frequency": frequency,
            "frequency_details": frequency_details
        }
        # Remove None values explicitly passed if you want partial updates
        # update_data = {k: v for k, v in update_data.items() if v is not None} # Optional based on PUT vs PATCH semantics

        return await self.reminder_repository.update(reminder_id, update_data)


    def _format_reminder(self, reminder: ReminderEntity) -> dict:
        return {
            "id": str(reminder.id),
            "user_id": reminder.user_id,
            "title": reminder.title,
            "time": reminder.time,
            "frequency": reminder.frequency,
            "frequency_details": reminder.frequency_details,
            "created_at": reminder.created_at.isoformat(),
        }