import unittest
import os
from unittest.mock import patch
from src.prometheus_orchestrator import PrometheusAgent

class TestPrometheusAgent(unittest.TestCase):
    def setUp(self):
        self.agent = PrometheusAgent()

    @patch('src.prometheus_orchestrator.requests.post')
    def test_openai_api_call(self, mock_post):
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {
            "choices": [{"message": {"content": "Mock OpenAI response"}}]
        }
        response = self.agent.openai_api_call("Test prompt")
        self.assertEqual(response, "Mock OpenAI response")

    @patch('src.prometheus_orchestrator.requests.post')
    def test_grok_api_call(self, mock_post):
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {
            "choices": [{"message": {"content": "Mock Grok response"}}]
        }
        response = self.agent.grok_api_call("Test prompt")
        self.assertEqual(response, "Mock Grok response")

    @patch('src.prometheus_orchestrator.Agent.run')
    def test_griptape_api_call(self, mock_run):
        mock_run.return_value.output_task.output.value = "Mock Griptape response"
        response = self.agent.griptape_api_call("Test prompt")
        self.assertEqual(response, "Mock Griptape response")

    def test_assign_task_griptape(self):
        with patch.object(self.agent, 'griptape_api_call', return_value="Griptape priority"):
            task_data = self.agent.assign_task("Test task", "Vitruvius")
            self.assertEqual(task_data["griptape_priority"], "Griptape priority")
            self.assertEqual(task_data["status"], "In Progress")

if __name__ == '__main__':
    unittest.main()