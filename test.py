try:
    from app import app
    import unittest2
except Exception as e:
    print("Some modules are missing {}".format(e))

class FlaskTest(unittest2.TestCase):
    #Check for response 302
    #reposnse 302 indicates found and redirected to other location
    def test_index(self):
        tester = app.test_client(self)
        response = tester.get("/")
        statuscode = response.status_code
        self.assertEqual(statuscode,302)
    #Check response 200
    def test_index2(self):
        tester = app.test_client(self)
        response = tester.get("/search")
        statuscode = response.status_code
        self.assertEqual(statuscode,200)


if __name__=="__main__":
    unittest2.main()
