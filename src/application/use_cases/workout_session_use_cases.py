from typing import List, Optional
from datetime import datetime

from ...domain.entities.workout_session import (
    WorkoutSessionEntity,
    ExerciseLog,
    StrengthSet,
    CardioSet,
)
from ...infrastructure.repositories.workout_session_repository import (
    WorkoutSessionRepository,
)
from ...infrastructure.repositories.workout_package_repository import (
    WorkoutPackageRepository,
)
from ...infrastructure.repositories.exercise_repository import ExerciseRepository
from ...infrastructure.repositories.user_repository import UserRepository

# --- Tabela básica de METs ---
MET_VALUES = {
    "strength": 6.0,      # musculação moderada/intensa
    "cardio": 7.0,        # cardio moderado (corrida, bicicleta, etc)
    "default": 5.0        # fallback
}

def calculate_calories(session_data: dict, weight_kg: Optional[float]) -> Optional[float]:
    """
    Calcula calorias queimadas com base nos dados da sessão de treino.
    Retorna None se o peso não for fornecido ou inválido.
    """
    if not weight_kg or weight_kg <= 0:
        return None # Retorna None se não houver peso válido

    exercises = session_data.get("exercises", [])
    duration_total_session = session_data.get("duration_minutes", None)
    total_calories = 0
    total_estimated_duration_from_exercises = 0
    calories_details = [] # Para ajuste proporcional

    for exercise in exercises:
        ex_type = exercise.get("type", "default")
        duration = 0

        if ex_type == "cardio" and exercise.get("sets"):
            # Usa a duração real do cardio se disponível
            cardio_duration = sum(s.get("duration_minutes", 0) for s in exercise["sets"] if isinstance(s.get("duration_minutes"), (int, float)))
            duration = cardio_duration if cardio_duration > 0 else 10 # Fallback 10 min se duração for 0 ou não encontrada
        elif ex_type == "strength":
            # Média de 3 minutos por série (execução + descanso)
            num_sets = len(exercise.get("sets", []))
            duration = num_sets * 3
        else: # Default or unknown type
            num_sets = len(exercise.get("sets", []))
            duration = max(num_sets * 2, 5) # Fallback menor para tipos desconhecidos

        # Pular se a duração for 0
        if duration <= 0:
            continue

        # Obter MET
        met = MET_VALUES.get(ex_type, MET_VALUES["default"])

        # Calorias = MET * peso (kg) * tempo (h)
        calories = met * weight_kg * (duration / 60)
        calories_details.append({"duration": duration, "calories": calories})
        total_estimated_duration_from_exercises += duration
        total_calories += calories

    # Ajuste proporcional se a duração total da SESSÃO estiver disponível e for diferente da soma das durações estimadas
    if duration_total_session and total_estimated_duration_from_exercises > 0 and duration_total_session != total_estimated_duration_from_exercises:
        adjustment = duration_total_session / total_estimated_duration_from_exercises
        total_calories *= adjustment

    return round(total_calories, 1)

class WorkoutSessionUseCases:
    def __init__(
        self,
        session_repository: WorkoutSessionRepository,
        package_repository: WorkoutPackageRepository,
        exercise_repository: ExerciseRepository,
        user_repository: UserRepository,
    ):
        self.session_repository = session_repository
        self.package_repository = package_repository
        self.exercise_repository = exercise_repository
        self.user_repository = user_repository

    async def start_session(self, user_id: str, package_id: str) -> str:
        """Start a new workout session"""
        # Get package details
        package = await self.package_repository.find_by_id(package_id)
        if not package:
            raise ValueError("Package not found")

        # Build exercise logs with exercise details
        exercise_logs = []
        for pkg_exercise in package.exercises:
            exercise = await self.exercise_repository.find_by_id(
                pkg_exercise.exercise_id
            )
            if exercise:
                exercise_logs.append(
                    ExerciseLog(
                        exercise_id=str(exercise.id),
                        exercise_name=exercise.name,
                        type=exercise.type,
                        sets=[],
                        notes=pkg_exercise.notes,
                    )
                )

        session = WorkoutSessionEntity(
            user_id=user_id,
            package_id=package_id,
            package_name=package.name,
            exercises=exercise_logs,
            is_completed=False,
        )

        return await self.session_repository.create(session)

    async def update_session(
        self, session_id: str, user_id: str, exercises: List[dict]
    ) -> bool:
        """Update session with exercise data"""
        session = await self.session_repository.find_by_id(session_id)
        if not session or session.user_id != user_id:
            raise ValueError("Session not found or unauthorized")

        # Update exercises
        updated_exercises = []
        for ex_data in exercises:
            sets = []
            for set_data in ex_data.get("sets", []):
                if ex_data["type"] == "strength":
                    sets.append(StrengthSet(**set_data))
                else:
                    sets.append(CardioSet(**set_data))

            updated_exercises.append(
                ExerciseLog(
                    exercise_id=ex_data["exercise_id"],
                    exercise_name=ex_data["exercise_name"],
                    type=ex_data["type"],
                    sets=sets,
                    notes=ex_data.get("notes"),
                )
            )

        session.exercises = updated_exercises
        return await self.session_repository.update(session_id, session)

    async def complete_session(self, session_id: str, user_id: str) -> bool:
        """Complete a workout session"""
        session = await self.session_repository.find_by_id(session_id)
        if not session or session.user_id != user_id:
            raise ValueError("Session not found or unauthorized")

        session.end_time = datetime.utcnow()
        session.is_completed = True

        # Calculate duration
        duration = (session.end_time - session.start_time).total_seconds() / 60
        session.duration_minutes = int(duration)

        return await self.session_repository.update(session_id, session)

    async def delete_session(self, session_id: str, user_id: str) -> bool:
        """Delete a workout session"""
        session = await self.session_repository.find_by_id(session_id)
        if not session or session.user_id != user_id:
            raise ValueError("Session not found or unauthorized")

        return await self.session_repository.delete(session_id)

    async def get_session(self, session_id: str, user_id: str) -> Optional[dict]:
        """Get session by ID"""
        session = await self.session_repository.find_by_id(session_id)
        if not session or session.user_id != user_id:
            return None

        user = await self.user_repository.find_by_id(user_id) # Buscar usuário para pegar o peso
        session_dict = session.model_dump() # Converter Pydantic model para dict

        # Calcular calorias
        total_calories = calculate_calories(session_dict, user.weight if user else None)

        # Formatar resposta
        return {
            "id": str(session.id),
            "user_id": session.user_id,
            "package_id": session.package_id,
            "package_name": session.package_name,
            "exercises": [
                {
                    "exercise_id": ex.exercise_id,
                    "exercise_name": ex.exercise_name,
                    "type": ex.type,
                    "sets": [s.model_dump() for s in ex.sets],
                    "notes": ex.notes,
                }
                for ex in session.exercises
            ],
            "start_time": session.start_time.isoformat(),
            "end_time": session.end_time.isoformat() if session.end_time else None,
            "duration_minutes": session.duration_minutes,
            "is_completed": session.is_completed,
            "total_calories": total_calories # Adicionar calorias
        }

    async def get_user_sessions(
        self, user_id: str, limit: int = 50, skip: int = 0
    ) -> List[dict]:
        """Get all sessions for a user"""
        sessions = await self.session_repository.find_by_user(user_id, limit, skip)
        user = await self.user_repository.find_by_id(user_id) # Buscar usuário uma vez
        weight = user.weight if user else None

        results = []
        for s in sessions:
            session_dict = s.model_dump()
            total_calories = calculate_calories(session_dict, weight)
            results.append({
                "id": str(s.id),
                "package_id": s.package_id,
                "package_name": s.package_name,
                "start_time": s.start_time.isoformat(),
                "end_time": s.end_time.isoformat() if s.end_time else None,
                "duration_minutes": s.duration_minutes,
                "is_completed": s.is_completed,
                "exercise_count": len(s.exercises),
                "total_calories": total_calories, # Adicionar calorias
            })
        return results

    async def get_sessions_by_date_range(
        self, user_id: str, start_date: datetime, end_date: datetime
    ) -> List[dict]:
        """Get sessions by date range"""
        sessions = await self.session_repository.find_by_user_and_date_range(
            user_id, start_date, end_date
        )
        user = await self.user_repository.find_by_id(user_id) # Buscar usuário uma vez
        weight = user.weight if user else None

        results = []
        for s in sessions:
             session_dict = s.model_dump()
             total_calories = calculate_calories(session_dict, weight)
             results.append({
                "id": str(s.id),
                "package_id": s.package_id,
                "package_name": s.package_name,
                "start_time": s.start_time.isoformat(),
                "end_time": s.end_time.isoformat() if s.end_time else None,
                "duration_minutes": s.duration_minutes,
                "is_completed": s.is_completed,
                "total_calories": total_calories, # Adicionar calorias
            })
        return results

    async def start_empty_session(self, user_id: str) -> str:
        """Starts a new empty workout session"""
        session = WorkoutSessionEntity(
            user_id=user_id,
            package_id="empty_session", # Use a special identifier
            package_name="Treino Livre",
            exercises=[],
            is_completed=False,
        )

        return await self.session_repository.create(session)

    async def get_all_user_sessions(self, user_id: str) -> List[dict]:
        """Get all sessions for a user, including active ones."""
        sessions = await self.session_repository.find_by_user(user_id, limit=1000) # Get all sessions
        user = await self.user_repository.find_by_id(user_id) # Buscar usuário uma vez
        weight = user.weight if user else None

        results = []
        for s in sessions:
            session_dict = s.model_dump()
            total_calories = calculate_calories(session_dict, weight)
            results.append({
                "id": str(s.id),
                "package_id": s.package_id,
                "package_name": s.package_name,
                "start_time": s.start_time.isoformat(),
                "end_time": s.end_time.isoformat() if s.end_time else None,
                "duration_minutes": s.duration_minutes,
                "is_completed": s.is_completed,
                "exercise_count": len(s.exercises),
                "total_calories": total_calories,
            })
        return results
        