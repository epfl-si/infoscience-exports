from locust import HttpLocust, TaskSet, task


def increment():
    increment.i += 1
    return increment.i


increment.i = 0


class Scenario1(TaskSet):
    @task(2)
    def create_export(self):
        response = self.client.get("/exports/new/")
        csrftoken = response.cookies.get('csrftoken')
        self.client.post("/exports/new/",
                         {"name": "Test%s" % increment(),
                          "csrfmiddlewaretoken": csrftoken}
                         )

    @task(60)
    def list_exports(self):
        self.client.get("/exports/")


class WebsiteUser(HttpLocust):
    host = "http://127.0.0.1:8000"
    task_set = Scenario1
    min_wait = 1000
    max_wait = 1000
