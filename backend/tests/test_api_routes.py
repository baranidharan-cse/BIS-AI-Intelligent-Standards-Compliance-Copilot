"""Tests for FastAPI HTTP routes using httpx AsyncClient."""
import pytest
from httpx import AsyncClient, ASGITransport
from app.main import create_app
from app.database import get_db


@pytest.mark.asyncio
async def test_api_routes(db):
    """Test API endpoints across health, materials, quizzes, learning paths, revision, chat, and progress."""
    app = create_app()

    # Override get_db dependency to use test db fixture
    async def override_get_db():
        yield db

    app.dependency_overrides[get_db] = override_get_db

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Health check
        res = await client.get("/api/health")
        assert res.status_code == 200
        assert res.json()["status"] == "ok"

        # 2. Material creation
        res = await client.post("/api/materials", json={
            "title": "API Test Material",
            "raw_text": "Python variables and data types",
            "description": "Created via API test"
        })
        assert res.status_code == 200
        mat_data = res.json()
        mat_id = mat_data["id"]

        # 3. List materials
        res = await client.get("/api/materials")
        assert res.status_code == 200
        assert len(res.json()) >= 1

        # 4. Get material detail & Explain topic
        res = await client.get(f"/api/materials/{mat_id}")
        assert res.status_code == 200

        res = await client.post("/api/materials/explain", json={
            "topic_name": "Variables",
            "context": "Python variables",
            "difficulty_level": "eli10"
        })
        assert res.status_code == 200
        assert "explanation" in res.json()

        # 5. Learning path generation
        res = await client.post("/api/learning-paths/generate", json={"material_id": mat_id})
        assert res.status_code == 200
        lp_data = res.json()
        assert len(lp_data["steps"]) > 0

        step_id = lp_data["steps"][0]["id"]
        res = await client.patch(f"/api/learning-paths/steps/{step_id}/status", json={"status": "completed"})
        assert res.status_code == 200

        # 6. Quiz generation & attempt
        res = await client.post("/api/quizzes/generate", json={"material_id": mat_id, "num_questions": 2})
        assert res.status_code == 200
        quiz_data = res.json()
        quiz_id = quiz_data["id"]

        res = await client.post(f"/api/quizzes/{quiz_id}/attempts", json={"answers": {}})
        assert res.status_code == 200

        # 7. Revision plan generation
        res = await client.post("/api/revision/plans/generate", json={"material_id": mat_id})
        assert res.status_code == 200

        res = await client.get("/api/revision/tasks/due")
        assert res.status_code == 200

        # 8. Chat
        res = await client.post("/api/chat/message", json={
            "session_id": "api-session",
            "message": "Hello tutor!",
            "material_id": mat_id
        })
        assert res.status_code == 200

        res = await client.get("/api/chat/sessions/api-session")
        assert res.status_code == 200
        assert len(res.json()) >= 2

        # 9. Dashboard & Profile progress
        res = await client.get("/api/progress/dashboard")
        assert res.status_code == 200
        assert "total_materials" in res.json()

        res = await client.get("/api/progress/profile")
        assert res.status_code == 200
        assert "badges" in res.json()

        # 10. Delete material
        res = await client.delete(f"/api/materials/{mat_id}")
        assert res.status_code == 200
        assert res.json()["deleted"] is True
