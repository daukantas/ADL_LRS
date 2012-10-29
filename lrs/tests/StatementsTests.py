from django.test import TestCase
from django.test.utils import setup_test_environment
from django.core.urlresolvers import reverse
from lrs import views, models
from os import path
import sys
import json
import base64
import uuid
from datetime import datetime, timedelta
from django.utils.timezone import utc
from lrs.objects import Activity, Statement
import time
import urllib
from lrs.util import retrieve_statement
import pdb
import hashlib

class StatementsTests(TestCase):
    def setUp(self):
        self.username = "tester1"
        self.email = "test1@tester.com"
        self.password = "test"
        self.auth = "Basic %s" % base64.b64encode("%s:%s" % (self.username, self.password))
        form = {"username":self.username, "email":self.email,"password":self.password,"password2":self.password}
        response = self.client.post(reverse(views.register),form, X_Experience_API_Version="0.95")

        self.guid1 = str(uuid.uuid4())
        self.guid2 = str(uuid.uuid4())
        self.guid3 = str(uuid.uuid4())    
        self.guid4 = str(uuid.uuid4())
        self.guid5 = str(uuid.uuid4())
        self.guid6 = str(uuid.uuid4())
        self.guid7 = str(uuid.uuid4())
        self.guid8 = str(uuid.uuid4())
        self.guid9 = str(uuid.uuid4())        
        self.cguid1 = str(uuid.uuid4())
        self.cguid2 = str(uuid.uuid4())    
        self.cguid3 = str(uuid.uuid4())
        self.cguid4 = str(uuid.uuid4())
        self.cguid5 = str(uuid.uuid4())
        self.cguid6 = str(uuid.uuid4())

        self.existStmt = Statement.Statement(json.dumps({"verb":{"id": "http://adlnet.gov/expapi/verbs/created",
            "display": {"en-US":"created"}}, "object": {"id":"activity"},
            "actor":{"objectType":"Agent","mbox":"s@s.com"},
            "authority":{"objectType":"Agent","name":"tester1","mbox":"test1@tester.com"}}))
        self.exist_stmt_id = self.existStmt.statement.statement_id

        self.firstTime = str(datetime.utcnow().replace(tzinfo=utc).isoformat())

        self.existStmt1 = json.dumps({"verb":{"id": "http://adlnet.gov/expapi/verbs/created",
            "display": {"en-US":"created"}},"actor":{"objectType":"Agent","mbox":"s@s.com"},
            "object": {"objectType": "Activity", "id":"foogie",
            "definition": {"name": {"en-US":"testname2", "en-GB": "altname"},
            "description": {"en-US":"testdesc2", "en-GB": "altdesc"}, "type": "cmi.interaction",
            "interactionType": "fill-in","correctResponsesPattern": ["answer"],
            "extensions": {"key1": "value1", "key2": "value2","key3": "value3"}}}, 
            "result": {"score":{"scaled":.85}, "completion": True, "success": True, "response": "kicked",
            "duration": self.firstTime, "extensions":{"key1": "value1", "key2":"value2"}},
            "context":{"registration": self.cguid1, "contextActivities": {"other": {"id": "NewActivityID2"}},
            "revision": "food", "platform":"bard","language": "en-US", "extensions":{"ckey1": "cval1",
            "ckey2": "cval2"}}})        

        self.existStmt2 = json.dumps({"verb":{"id": "http://adlnet.gov/expapi/verbs/created",
            "display": {"en-US":"created"}},"actor":{"objectType":"Agent","mbox":"s@t.com"},
            "object": {"objectType": "Activity", "id":"foogie",
            "definition": {"name": {"en-US":"testname3", "en-GB": "altname"},
            "description": {"en-US":"testdesc3","en-GB":"altdesc"}, "type": "cmi.interaction",
            "interactionType": "fill-in","correctResponsesPattern": ["answers"],
            "extensions": {"key11": "value11", "key22": "value22","key33": "value33"}}}, 
            "result": {"score":{"scaled":.75}, "completion": True, "success": True, "response": "shouted",
            "duration": self.firstTime, "extensions":{"dkey1": "dvalue1", "dkey2":"dvalue2"}},
            "context":{"registration": self.cguid2, "contextActivities": {"other": {"id": "NewActivityID22"}},
            "revision": "food", "platform":"bard","language": "en-US", "extensions":{"ckey11": "cval11",
            "ckey22": "cval22"}}})        

        self.existStmt3 = json.dumps({"verb":{"id": "http://adlnet.gov/expapi/verbs/created",
            "display": {"en-US":"created"}},"actor":{"objectType":"Agent","mbox":"s@s.com"},
            "object": {"objectType": "Activity", "id":"foogals",
            "definition": {"name": {"en-US":"testname3"},"description": {"en-US":"testdesc3"}, "type": "cmi.interaction",
            "interactionType": "fill-in","correctResponsesPattern": ["answers"],
            "extensions": {"key111": "value111", "key222": "value222","key333": "value333"}}}, 
            "result": {"score":{"scaled":.79}, "completion": True, "success": True, "response": "shouted",
            "duration": self.firstTime, "extensions":{"dkey1": "dvalue1", "dkey2":"dvalue2"}},
            "context":{"registration": self.cguid3, "contextActivities": {"other": {"id": "NewActivityID22"}},
            "revision": "food", "platform":"bard","language": "en-US",
            "instructor":{"objectType": "Agent", "name":"bob", "mbox":"bob@bob.com"}, 
            "extensions":{"ckey111": "cval111","ckey222": "cval222"}}})        

        self.existStmt4 = json.dumps({"verb":{"id": "http://adlnet.gov/expapi/verbs/created",
            "display": {"en-US":"created"}},"actor":{"objectType":"Agent","mbox":"s@s.com"},
            "object": {"objectType": "Activity", "id":"foogal",
            "definition": {"name": {"en-US":"testname3"},"description": {"en-US":"testdesc3"}, "type": "cmi.interaction",
            "interactionType": "fill-in","correctResponsesPattern": ["answers"],
            "extensions": {"key111": "value111", "key222": "value222","key333": "value333"}}}, 
            "result": {"score":{"scaled":.79}, "completion": True, "success": True, "response": "shouted",
            "duration": self.firstTime, "extensions":{"dkey1": "dvalue1", "dkey2":"dvalue2"}},
            "context":{"registration": self.cguid4, "contextActivities": {"other": {"id": "NewActivityID22"}},
            "revision": "food", "platform":"bard","language": "en-US","instructor":{"name":"bill", "mbox":"bill@bill.com"},
            "extensions":{"ckey111": "cval111","ckey222": "cval222"}}})

        self.existStmt5 = json.dumps({"object":{"objectType":"Agent","name":"jon","mbox":"jon@jon.com"},
            "verb":{"id": "http://adlnet.gov/expapi/verbs/created","display": {"en-US":"created"}},
            "actor":{"objectType":"Agent","mbox":"s@s.com"}})

        self.existStmt6 = json.dumps({"actor": {"objectType":"Agent","name":"max","mbox":"max@max.com"}, 
                                      "object":{"id": "test_activity"},"verb":{"id": "http://adlnet.gov/expapi/verbs/created",
                                      "display": {"en-US":"created"}}})

        self.existStmt7 = json.dumps({"object": {"objectType":"Agent","name":"max","mbox":"max@max.com"},
            "verb": {"id": "http://adlnet.gov/expapi/verbs/created","display": {"en-US":"created"}},
            "actor":{"objectType":"Agent","mbox":"s@s.com"}})

        self.existStmt8 = json.dumps({"object": {"objectType":"Agent","name":"john","mbox":"john@john.com"},
            "verb": {"id": "http://adlnet.gov/expapi/verbs/missed","display": {"en-US":"missed"}},
            "actor":{"objectType":"Agent","mbox":"s@s.com"}})

        self.existStmt9 = json.dumps({"actor":{"objectType":"Agent","mbox":"sub@sub.com"},
            "verb":{"id": "http://adlnet.gov/expapi/verbs/missed"},"object":{"objectType":"SubStatement",
            "actor":{"objectType":"Agent","mbox":"ss@ss.com"},"verb": {"id":"verb/url/nested"},
            "object": {"objectType":"activity", "id":"testex.com"}, "result":{"completion": True, "success": True,
            "response": "kicked"}, "context":{"registration": self.cguid6,
            "contextActivities": {"other": {"id": "NewActivityID"}},"revision": "foo", "platform":"bar",
            "language": "en-US", "extensions":{"k1": "v1", "k2": "v2"}}}})

        # Put statements
        param = {"statementId":self.guid1}
        path = "%s?%s" % (reverse(views.statements), urllib.urlencode(param))
        stmt_payload = self.existStmt1
        self.putresponse1 = self.client.put(path, stmt_payload, content_type="application/json", Authorization=self.auth, X_Experience_API_Version="0.95")
        self.assertEqual(self.putresponse1.status_code, 204)
        time = retrieve_statement.convertToUTC(str((datetime.utcnow()+timedelta(seconds=2)).replace(tzinfo=utc).isoformat()))
        stmt = models.statement.objects.filter(statement_id=self.guid1).update(stored=time)


        param = {"statementId":self.guid3}
        path = "%s?%s" % (reverse(views.statements), urllib.urlencode(param))
        stmt_payload = self.existStmt3
        self.putresponse3 = self.client.put(path, stmt_payload, content_type="application/json", Authorization=self.auth, X_Experience_API_Version="0.95")
        self.assertEqual(self.putresponse3.status_code, 204)
        time = retrieve_statement.convertToUTC(str((datetime.utcnow()+timedelta(seconds=3)).replace(tzinfo=utc).isoformat()))
        stmt = models.statement.objects.filter(statement_id=self.guid3).update(stored=time)

        
        param = {"statementId":self.guid4}
        path = "%s?%s" % (reverse(views.statements), urllib.urlencode(param))
        stmt_payload = self.existStmt4
        self.putresponse4 = self.client.put(path, stmt_payload, content_type="application/json", Authorization=self.auth, X_Experience_API_Version="0.95")
        self.assertEqual(self.putresponse4.status_code, 204)
        time = retrieve_statement.convertToUTC(str((datetime.utcnow()+timedelta(seconds=4)).replace(tzinfo=utc).isoformat()))
        stmt = models.statement.objects.filter(statement_id=self.guid4).update(stored=time)

        self.secondTime = str((datetime.utcnow()+timedelta(seconds=4)).replace(tzinfo=utc).isoformat())
        
        param = {"statementId":self.guid2}
        path = "%s?%s" % (reverse(views.statements), urllib.urlencode(param))
        stmt_payload = self.existStmt2
        self.putresponse2 = self.client.put(path, stmt_payload, content_type="application/json", Authorization=self.auth, X_Experience_API_Version="0.95")       
        self.assertEqual(self.putresponse2.status_code, 204)
        time = retrieve_statement.convertToUTC(str((datetime.utcnow()+timedelta(seconds=6)).replace(tzinfo=utc).isoformat()))
        stmt = models.statement.objects.filter(statement_id=self.guid2).update(stored=time)


        param = {"statementId":self.guid5}
        path = "%s?%s" % (reverse(views.statements), urllib.urlencode(param))
        stmt_payload = self.existStmt5
        self.putresponse5 = self.client.put(path, stmt_payload, content_type="application/json", Authorization=self.auth, X_Experience_API_Version="0.95")
        self.assertEqual(self.putresponse5.status_code, 204)
        time = retrieve_statement.convertToUTC(str((datetime.utcnow()+timedelta(seconds=7)).replace(tzinfo=utc).isoformat()))
        stmt = models.statement.objects.filter(statement_id=self.guid5).update(stored=time)
        

        param = {"statementId":self.guid6}
        path = "%s?%s" % (reverse(views.statements), urllib.urlencode(param))
        stmt_payload = self.existStmt6
        self.putresponse6 = self.client.put(path, stmt_payload, content_type="application/json", Authorization=self.auth, X_Experience_API_Version="0.95")
        self.assertEqual(self.putresponse6.status_code, 204)
        time = retrieve_statement.convertToUTC(str((datetime.utcnow()+timedelta(seconds=8)).replace(tzinfo=utc).isoformat()))
        stmt = models.statement.objects.filter(statement_id=self.guid6).update(stored=time)

        
        param = {"statementId":self.guid7}
        path = "%s?%s" % (reverse(views.statements), urllib.urlencode(param))
        stmt_payload = self.existStmt7        
        self.putresponse7 = self.client.put(path, stmt_payload,  content_type="application/json", Authorization=self.auth, X_Experience_API_Version="0.95")
        self.assertEqual(self.putresponse7.status_code, 204)
        time = retrieve_statement.convertToUTC(str((datetime.utcnow()+timedelta(seconds=9)).replace(tzinfo=utc).isoformat()))
        stmt = models.statement.objects.filter(statement_id=self.guid7).update(stored=time)
        

        param = {"statementId":self.guid8}
        path = "%s?%s" % (reverse(views.statements), urllib.urlencode(param))
        stmt_payload = self.existStmt8        
        self.putresponse8 = self.client.put(path, stmt_payload, content_type="application/json", Authorization=self.auth, X_Experience_API_Version="0.95")
        self.assertEqual(self.putresponse8.status_code, 204)
        time = retrieve_statement.convertToUTC(str((datetime.utcnow()+timedelta(seconds=10)).replace(tzinfo=utc).isoformat()))
        stmt = models.statement.objects.filter(statement_id=self.guid8).update(stored=time)
        
        param = {"statementId": self.guid9}
        path = "%s?%s" % (reverse(views.statements), urllib.urlencode(param))
        stmt_payload = self.existStmt9        
        self.putresponse9 = self.client.put(path, stmt_payload, content_type="application/json", Authorization=self.auth, X_Experience_API_Version="0.95")
        self.assertEqual(self.putresponse9.status_code, 204)
        time = retrieve_statement.convertToUTC(str((datetime.utcnow()+timedelta(seconds=11)).replace(tzinfo=utc).isoformat()))
        stmt = models.statement.objects.filter(statement_id=self.guid9).update(stored=time)
        # stmt = models.statement.objects.filter(statement_id=self.guid9)[0]
        # sub = models.SubStatement.objects.get(id=stmt.stmt_object.id)
        # act = models.activity.objects.get(id=sub.stmt_object.id)


    def test_post_with_no_valid_params(self):
        # Error will be thrown in statements class
        resp = self.client.post(reverse(views.statements), {"feet":"yes","hands": {"id":"http://example.com/test_post"}},
            content_type="application/json", Authorization=self.auth, X_Experience_API_Version="0.95")
        self.assertEqual(resp.status_code, 400)

    def test_post(self):
        stmt = json.dumps({"actor":{"objectType": "Agent", "mbox":"t@t.com", "name":"bob"},
            "verb":{"id": "http://adlnet.gov/expapi/verbs/passed","display": {"en-US":"passed"}},
            "object": {"id":"test_post"}})
        response = self.client.post(reverse(views.statements), stmt, content_type="application/json",
            Authorization=self.auth, X_Experience_API_Version="0.95")
        
        self.assertEqual(response.status_code, 200)
        act = models.activity.objects.get(activity_id="test_post")
        self.assertEqual(act.activity_id, "test_post")
        agent = models.agent.objects.get(mbox="t@t.com")
        self.assertEqual(agent.name, "bob")

    def test_post_with_actor(self):
        stmt = json.dumps({"actor":{"mbox":"mailto:mr.t@example.com"},
            "verb":{"id": "http://adlnet.gov/expapi/verbs/passed","display": {"en-US":"passed"}},
            "object": {"id":"i.pity.the.fool"}})
        
        response = self.client.post(reverse(views.statements), stmt, content_type="application/json", Authorization=self.auth, X_Experience_API_Version="0.95")
        self.assertEqual(response.status_code, 200)
        agent = models.agent.objects.get(mbox="mailto:mr.t@example.com")

    def test_list_post(self):
        stmts = json.dumps([{"verb":{"id": "http://adlnet.gov/expapi/verbs/passed","display": {"en-US":"passed"}},
            "object": {"id":"test_list_post"}, "actor":{"objectType":"Agent", "mbox":"t@t.com"}},
            {"verb":{"id": "http://adlnet.gov/expapi/verbs/failed","display": {"en-GB":"failed"}},
            "object": {"id":"test_list_post1"}, "actor":{"objectType":"Agent", "mbox":"t@t.com"}}])
        
        response = self.client.post(reverse(views.statements), stmts,  content_type="application/json", Authorization=self.auth, X_Experience_API_Version="0.95")
        self.assertEqual(response.status_code, 200)
        activity1 = models.activity.objects.get(activity_id="test_list_post")
        activity2 = models.activity.objects.get(activity_id="test_list_post1")
        stmt1 = models.statement.objects.get(stmt_object=activity1)
        stmt2 = models.statement.objects.get(stmt_object=activity2)
        verb1 = models.Verb.objects.get(id=stmt1.statement.verb.id)
        verb2 = models.Verb.objects.get(id=stmt2.statement.verb.id)
        lang_map1 = verb1.display.all()[0]
        lang_map2 = verb2.display.all()[0]

        self.assertEqual(response.status_code, 200)
        self.assertEqual(stmt1.verb.verb_id, "http://adlnet.gov/expapi/verbs/passed")
        self.assertEqual(stmt2.verb.verb_id, "http://adlnet.gov/expapi/verbs/failed")
        
        self.assertEqual(lang_map1.key, "en-US")
        self.assertEqual(lang_map1.value, "passed")
        self.assertEqual(lang_map2.key, "en-GB")
        self.assertEqual(lang_map2.value, "failed")


    def test_put(self):
        guid = str(uuid.uuid4())

        param = {"statementId":guid}
        path = "%s?%s" % (reverse(views.statements), urllib.urlencode(param))
        stmt = json.dumps({"verb":{"id": "http://adlnet.gov/expapi/verbs/passed","display": {"en-US":"passed"}},
            "object": {"id":"test_put"},"actor":{"objectType":"Agent", "mbox":"t@t.com"}})

        putResponse = self.client.put(path, stmt, content_type="application/json", Authorization=self.auth, X_Experience_API_Version="0.95")
        self.assertEqual(putResponse.status_code, 204)
        stmt = models.statement.objects.get(statement_id=guid)

        act = models.activity.objects.get(activity_id="test_put")
        self.assertEqual(act.activity_id, "test_put")

        self.assertEqual(stmt.statement.actor.mbox, "t@t.com")

        self.assertEqual(stmt.statement.authority.name, "tester1")
        self.assertEqual(stmt.statement.authority.mbox, "test1@tester.com")
        
        
        self.assertEqual(stmt.verb.verb_id, "http://adlnet.gov/expapi/verbs/passed")

    def test_put_with_substatement(self):
        con_guid = str(uuid.uuid4())
        st_guid = str(uuid.uuid4())

        param = {"statementId": st_guid}
        path = "%s?%s" % (reverse(views.statements), urllib.urlencode(param))
        stmt = json.dumps({"actor":{"objectType":"Agent","mbox":"sass@sass.com"},
            "verb": {"id":"verb/url/tested"}, "object":{"objectType":"SubStatement",
            "actor":{"objectType":"Agent","mbox":"ss@ss.com"},"verb": {"id":"verb/url/nested"},
            "object": {"objectType":"activity", "id":"testex.com"}, "result":{"completion": True, "success": True,
            "response": "kicked"}, "context":{"registration": con_guid,
            "contextActivities": {"other": {"id": "NewActivityID"}},"revision": "foo", "platform":"bar",
            "language": "en-US", "extensions":{"k1": "v1", "k2": "v2"}}}})
        
        response = self.client.put(path, stmt, content_type="application/json",
            Authorization=self.auth, X_Experience_API_Version="0.95")
        self.assertEqual(response.status_code, 204)

        path = "%s?%s" % (reverse(views.statements), urllib.urlencode(param))        
        get_response = self.client.get(path, X_Experience_API_Version="0.95", Authorization=self.auth)

        self.assertEqual(get_response.status_code, 200)
        self.assertContains(get_response, "objectType")
        self.assertContains(get_response, "SubStatement")
        self.assertContains(get_response, "actor")
        self.assertContains(get_response, "ss@ss.com")
        self.assertContains(get_response, "verb")
        self.assertContains(get_response, "verb/url/nested")
        self.assertContains(get_response, "Activity")
        self.assertContains(get_response, "testex.com")
        self.assertContains(get_response, "result")
        self.assertContains(get_response, "completion")
        self.assertContains(get_response, "success")
        self.assertContains(get_response, "response")
        self.assertContains(get_response, "kicked")
        self.assertContains(get_response, "context")
        self.assertContains(get_response, con_guid)
        self.assertContains(get_response, "contextActivities")
        self.assertContains(get_response, "other")
        self.assertContains(get_response, "revision")
        self.assertContains(get_response, "foo")
        self.assertContains(get_response, "platform")
        self.assertContains(get_response, "bar")
        self.assertContains(get_response, "language")
        self.assertContains(get_response, "en-US")
        self.assertContains(get_response, "extensions")
        self.assertContains(get_response, "k1")
        self.assertContains(get_response, "v1")
        self.assertContains(get_response, "k2")
        self.assertContains(get_response, "v2")                                                                                                                                                                                                                

    def test_no_content_put(self):
        guid = str(uuid.uuid4())
        
        param = {"statementId":guid}
        path = "%s?%s" % (reverse(views.statements), urllib.urlencode(param))        
        stmt = json.dumps({})

        putResponse = self.client.put(path, stmt, content_type="application/json", Authorization=self.auth, X_Experience_API_Version="0.95")
        self.assertEqual(putResponse.status_code, 400)

    def test_existing_stmtID_put(self):
        guid = str(uuid.uuid4())

        existStmt = Statement.Statement(json.dumps({"statement_id":guid,
            "verb":{"id": "http://adlnet.gov/expapi/verbs/passed","display": {"en-US":"passed"}},
            "object": {"id":"activity"},"actor":{"objectType":"Agent", "mbox":"t@t.com"}}))

        param = {"statementId":guid}
        path = "%s?%s" % (reverse(views.statements), urllib.urlencode(param))        
        stmt = json.dumps({"verb":{"id": "http://adlnet.gov/expapi/verbs/passed","display": {"en-US":"passed"}},
            "object":{"id":"test_existing_put"}, "actor":{"objectType":"Agent", "mbox":"t@t.com"}})

        putResponse = self.client.put(path, stmt, content_type="application/json", Authorization=self.auth, X_Experience_API_Version="0.95")
        
        self.assertEqual(putResponse.status_code, 409)        

    def test_missing_stmtID_put(self):        
        stmt = json.dumps({"verb":{"id": "http://adlnet.gov/expapi/verbs/passed","display": {"en-US":"passed"}},
            "object": {"id":"test_put"},"actor":{"objectType":"Agent", "mbox":"t@t.com"}})
        response = self.client.put(reverse(views.statements), stmt, content_type="application/json", Authorization=self.auth, X_Experience_API_Version="0.95")
        self.assertEqual(response.status_code, 400)
        self.assertIn(response.content, "Error -- statements - method = PUT, but statementId paramater is missing")

    def test_get(self):
        param = {"statementId":self.guid1}
        path = "%s?%s" % (reverse(views.statements), urllib.urlencode(param))        
        getResponse = self.client.get(path, X_Experience_API_Version="0.95", Authorization=self.auth)
        self.assertEqual(getResponse.status_code, 200)
        self.assertContains(getResponse, self.guid1)

    # def test_get_wrong_auth(self):
    #     username = "tester2"
    #     email = "test2@tester.com"
    #     password = "test"
    #     auth = "Basic %s" % base64.b64encode("%s:%s" % (username, password))
    #     form = {"username":username, "email":email,"password":password,"password2":password}
    #     response = self.client.post(reverse(views.register),form, X_Experience_API_Version="0.95")

    #     param = {"statementId":self.guid1}
    #     path = "%s?%s" % (reverse(views.statements), urllib.urlencode(param))        
    #     getResponse = self.client.get(path, X_Experience_API_Version="0.95", Authorization=auth)
    #     self.assertEqual(getResponse.status_code, 403)

    def test_get_no_existing_ID(self):
        param = {"statementId":"aaaaaa"}
        path = "%s?%s" % (reverse(views.statements), urllib.urlencode(param))        
        getResponse = self.client.get(path, X_Experience_API_Version="0.95", Authorization=self.auth)
        self.assertEqual(getResponse.status_code, 404)

    def test_get_no_auth(self):
        param = {"statementId":self.guid1}
        path = "%s?%s" % (reverse(views.statements), urllib.urlencode(param))        
        getResponse = self.client.get(path, X_Experience_API_Version="0.95")
        self.assertEqual(getResponse.status_code, 401)

    def test_get_no_statementid(self):
        getResponse = self.client.get(reverse(views.statements), X_Experience_API_Version="0.95", Authorization=self.auth)
        self.assertEqual(getResponse.status_code, 200)
        jsn = json.loads(getResponse.content)
        self.assertEqual(len(jsn["statements"]), models.statement.objects.all().count())
        
    def test_since_filter(self):
        # Test since - should only get existStmt1-8 since existStmt is stored at same time as firstTime
        param = {"since": self.firstTime}
        path = "%s?%s" % (reverse(views.statements), urllib.urlencode(param))        
        sinceGetResponse = self.client.get(path, X_Experience_API_Version="0.95", Authorization=self.auth)

        self.assertEqual(sinceGetResponse.status_code, 200)
        self.assertContains(sinceGetResponse, self.guid1)
        self.assertContains(sinceGetResponse, self.guid2)
        self.assertContains(sinceGetResponse, self.guid3)
        self.assertContains(sinceGetResponse, self.guid4)
        self.assertContains(sinceGetResponse, self.guid5)
        self.assertContains(sinceGetResponse, self.guid6)
        self.assertContains(sinceGetResponse, self.guid7)
        self.assertContains(sinceGetResponse, self.guid8)

    def test_until_filter(self):
        # Test until
        param = {"until": self.secondTime}
        path = "%s?%s" % (reverse(views.statements), urllib.urlencode(param))        
        untilGetResponse = self.client.get(path, X_Experience_API_Version="0.95", Authorization=self.auth)
 
        self.assertEqual(untilGetResponse.status_code, 200)
        self.assertContains(untilGetResponse, self.guid1)
        self.assertContains(untilGetResponse, self.guid3)
        self.assertContains(untilGetResponse, self.guid4)
        self.assertNotIn(self.guid2, untilGetResponse)
        self.assertNotIn(self.guid5, untilGetResponse)
        self.assertNotIn(self.guid6, untilGetResponse)
        self.assertNotIn(self.guid7, untilGetResponse)
        self.assertNotIn(self.guid8, untilGetResponse)

    def test_activity_object_filter(self):
        # Test activity object
        param = {"object":{"objectType": "Activity", "id":"foogie"}}
        path = "%s?%s" % (reverse(views.statements), urllib.urlencode(param))        
        activityObjectGetResponse = self.client.get(path, X_Experience_API_Version="0.95", Authorization=self.auth)

        self.assertEqual(activityObjectGetResponse.status_code, 200)
        self.assertContains(activityObjectGetResponse, self.guid1)
        self.assertContains(activityObjectGetResponse, self.guid2)
        self.assertNotIn(self.guid3, activityObjectGetResponse)
        self.assertNotIn(self.guid4, activityObjectGetResponse)
        self.assertNotIn(self.guid5, activityObjectGetResponse)
        self.assertNotIn(self.guid6, activityObjectGetResponse)
        self.assertNotIn(self.guid7, activityObjectGetResponse)
        self.assertNotIn(self.guid8, activityObjectGetResponse)
        # Should not be in response since sparse is true
        self.assertNotIn("testdesc3", activityObjectGetResponse)
        self.assertNotIn("testname3", activityObjectGetResponse)

    def test_no_actor(self):
        # Test actor object
        param = {"object":{"objectType": "Agent", "mbox":"nobody@example.com"}}
        path = "%s?%s" % (reverse(views.statements), urllib.urlencode(param))        
        actorObjectGetResponse = self.client.get(path, X_Experience_API_Version="0.95", Authorization=self.auth)
        
        self.assertEqual(actorObjectGetResponse.status_code, 200)
        stmts = json.loads(actorObjectGetResponse.content)
        dbstmts = models.statement.objects.all()
        self.assertEqual(len(stmts["statements"]), len(dbstmts))

    # def test_verb_filter(self):
    #     param = {"verb":"http://adlnet.gov/expapi/verbs/missed"}
    #     path = "%s?%s" % (reverse(views.statements), urllib.urlencode(param))        
    #     verb_response = self.client.get(path, X_Experience_API_Version="0.95")

    #     self.assertEqual(verb_response.status_code, 200)
    #     self.assertContains(verb_response, self.guid8)
    #     self.assertNotIn(self.guid7, verb_response)
    #     self.assertNotIn(self.guid6, verb_response)
    #     self.assertNotIn(self.guid5, verb_response)
    #     self.assertNotIn(self.guid4, verb_response)
    #     self.assertNotIn(self.guid2, verb_response)
    #     self.assertNotIn(self.guid3, verb_response)
    #     self.assertNotIn(self.guid1, verb_response)


    def test_actor_object_filter(self):
        # Test actor object
        param = {"object":{"objectType": "Agent", "name":"jon","mbox":"jon@jon.com"}}
        path = "%s?%s" % (reverse(views.statements), urllib.urlencode(param))        
        actorObjectGetResponse = self.client.get(path, X_Experience_API_Version="0.95", Authorization=self.auth)
        
        self.assertEqual(actorObjectGetResponse.status_code, 200)
        self.assertContains(actorObjectGetResponse, self.guid5)
        self.assertNotIn(self.guid4, actorObjectGetResponse)
        self.assertNotIn(self.guid2, actorObjectGetResponse)
        self.assertNotIn(self.guid3, actorObjectGetResponse)
        self.assertNotIn(self.guid1, actorObjectGetResponse)

    # TODO
    def test_substatement_object_filter(self):
        param = {"object":{"objectType": "SubStatement", "actor":{"objectType":"Agent","mbox":"ss@ss.com"},
        "verb": {"id":"verb/url/nested"},"object":{"objectType":"activity", "id":"testex.com"},
        "result":{"completion": True, "success": True,"response": "kicked"},"context":{"registration": self.cguid6,
            "contextActivities": {"other": {"id": "NewActivityID"}},"revision": "foo", "platform":"bar",
            "language": "en-US"}}}
            
        path = "%s?%s" % (reverse(views.statements), urllib.urlencode(param))        
        sub_object_get_response = self.client.get(path, X_Experience_API_Version="0.95", Authorization=self.auth)
        # print sub_object_get_response


    def test_registration_filter(self):
        # Test Registration
        param = {"registration": self.cguid4}
        path = "%s?%s" % (reverse(views.statements), urllib.urlencode(param))        
        registrationPostResponse = self.client.get(path, X_Experience_API_Version="0.95", Authorization=self.auth)

        self.assertEqual(registrationPostResponse.status_code, 200)
        self.assertContains(registrationPostResponse,self.guid4)
        self.assertNotIn(self.guid2, registrationPostResponse)
        self.assertNotIn(self.guid3, registrationPostResponse)
        self.assertNotIn(self.guid1, registrationPostResponse)
        self.assertNotIn(self.guid5, registrationPostResponse)
        self.assertNotIn(self.guid6, registrationPostResponse)
        self.assertNotIn(self.guid7, registrationPostResponse)
        self.assertNotIn(self.guid8, registrationPostResponse)

    def test_ascending_filter(self):
        # Test actor
        ascending_get_response = self.client.get(reverse(views.statements), 
            {"ascending": True},content_type="application/x-www-form-urlencoded", X_Experience_API_Version="0.95", Authorization=self.auth)

        self.assertEqual(ascending_get_response.status_code, 200)
        self.assertContains(ascending_get_response,self.guid1)
        self.assertContains(ascending_get_response,self.guid2)
        self.assertContains(ascending_get_response,self.guid3)
        self.assertContains(ascending_get_response,self.guid4)
        self.assertContains(ascending_get_response,self.guid5)
        self.assertContains(ascending_get_response,self.guid6)
        self.assertContains(ascending_get_response,self.guid7)
        self.assertContains(ascending_get_response,self.guid8)
        self.assertContains(ascending_get_response, str(self.exist_stmt_id))

    def test_actor_filter(self):
        # Test actor
        actorGetResponse = self.client.post(reverse(views.statements), 
            {"actor":{"objectType": "Agent", "mbox":"s@s.com"}},
             content_type="application/x-www-form-urlencoded", X_Experience_API_Version="0.95", Authorization=self.auth)
        
        self.assertEqual(actorGetResponse.status_code, 200)
        self.assertContains(actorGetResponse,self.guid1)
        self.assertContains(actorGetResponse,self.guid3)
        self.assertContains(actorGetResponse,self.guid4)                        
        self.assertNotIn(self.guid5, actorGetResponse)
        self.assertNotIn(self.guid6, actorGetResponse)
        self.assertNotIn(self.guid7, actorGetResponse)
        self.assertNotIn(self.guid8, actorGetResponse)                
        self.assertNotIn(self.guid2, actorGetResponse)

    # def test_instructor_filter(self):
    #     # Test instructor - will only return one b/c actor in stmt supercedes instructor in context
    #     instructorGetResponse = self.client.post(reverse(views.statements), 
    #                                             {"instructor":{"name":"bill","mbox":"bill@bill.com"}},  
    #                                             content_type="application/x-www-form-urlencoded", X_Experience_API_Version="0.95")
        
    #     self.assertEqual(instructorGetResponse.status_code, 200)
    #     self.assertContains(instructorGetResponse, self.guid4)
    #     self.assertNotIn(self.guid2, instructorGetResponse)
    #     self.assertNotIn(self.guid3, instructorGetResponse)
    #     self.assertNotIn(self.guid1, instructorGetResponse)
    #     self.assertNotIn(self.guid5, instructorGetResponse)
    #     self.assertNotIn(self.guid4, instructorGetResponse)
    #     self.assertNotIn(self.guid6, instructorGetResponse)
    #     self.assertNotIn(self.guid7, instructorGetResponse)
    #     self.assertNotIn(self.guid8, instructorGetResponse)

    def test_authoritative_filter(self):
        # Test authoritative
        self.username = "tester1"
        self.email = "test1@tester.com"
        self.password = "test"
        self.auth = "Basic %s" % base64.b64encode("%s:%s" % (self.username, self.password))
        form = {"username":self.username, "email":self.email,"password":self.password,"password2":self.password}
        response = self.client.post(reverse(views.register),form, X_Experience_API_Version="0.95")
        
        auth_stmt = json.dumps({"verb":{"id": "http://adlnet.gov/expapi/verbs/passed",
            "display": {"en-US":"created"}},"actor":{"objectType":"Agent","mbox":"s@s.com"},
            "object": {"objectType": "Activity", "id":"foogie",
            "definition": {"name": {"en-US":"testname2", "en-GB": "altname"},
            "description": {"en-US":"testdesc2", "en-GB": "altdesc"}, "type": "cmi.interaction",
            "interactionType": "fill-in","correctResponsesPattern": ["answer"],
            "extensions": {"key1": "value1", "key2": "value2","key3": "value3"}}}, 
            "result": {"score":{"scaled":.85}, "completion": True, "success": True, "response": "kicked",
            "duration": self.firstTime, "extensions":{"key1": "value1", "key2":"value2"}},
            "context":{"registration": self.cguid1, "contextActivities": {"other": {"id": "NewActivityID2"}},
            "revision": "food", "platform":"bard","language": "en-US", "extensions":{"ckey1": "cval1",
            "ckey2": "cval2"}}})

        post_response = self.client.post(reverse(views.statements), auth_stmt, content_type="application/json",
            Authorization=self.auth, X_Experience_API_Version="0.95")
        self.assertEqual(post_response.status_code, 200)

        params = {"authoritative": False, "actor":{"objectType":"Agent","mbox":"s@s.com"},
            "object":{"objectType": "Activity", "id":"foogie",
            "definition": {"name": {"en-US":"testname2", "en-GB": "altname"},
            "description": {"en-US":"testdesc2", "en-GB": "altdesc"}, "type": "cmi.interaction",
            "interactionType": "fill-in","correctResponsesPattern": ["answer"],
            "extensions": {"key1": "value1", "key2": "value2","key3": "value3"}}}}

        path = "%s?%s" % (reverse(views.statements), urllib.urlencode(params))        
        auth_get_response = self.client.get(path, X_Experience_API_Version="0.95", Authorization=self.auth)        
        self.assertEqual(auth_get_response.status_code, 200)
        
        stmts = json.loads(auth_get_response.content)
        self.assertEqual(len(stmts["statements"]), 2)

    def test_limit_filter(self):
        # Test limit
        limitGetResponse = self.client.post(reverse(views.statements),{"limit":1}, content_type="application/x-www-form-urlencoded", X_Experience_API_Version="0.95", Authorization=self.auth)
        respList = json.loads(limitGetResponse.content)
        stmts = respList["statements"]
        self.assertEqual(len(stmts), 1)
        self.assertContains(limitGetResponse, self.guid9)

    def test_sparse_filter(self):
        # Test sparse
        sparseGetResponse = self.client.post(reverse(views.statements),{"sparse": False}, content_type="application/x-www-form-urlencoded", X_Experience_API_Version="0.95", Authorization=self.auth)
        self.assertEqual(sparseGetResponse.status_code, 200)
        self.assertContains(sparseGetResponse, "definition")        
        self.assertContains(sparseGetResponse, "en-GB")
        self.assertContains(sparseGetResponse, "altdesc")
        self.assertContains(sparseGetResponse, "altname")


        # Should display full lang map (won"t find testdesc2 since activity class will merge activities with same id together)
        self.assertContains(sparseGetResponse, "testdesc3")

    # def test_linked_filters(self):
    #     # Test reasonable linked query
    #     param = {"verb":"http://adlnet.gov/expapi/verbs/created", "object":{"objectType": "Activity", "id":"foogie"}, "since":self.secondTime, "authoritative":"False", "sparse": False}
    #     path = "%s?%s" % (reverse(views.statements), urllib.urlencode(param))        
    #     linkedGetResponse = self.client.get(path, X_Experience_API_Version="0.95")
    #     self.assertEqual(linkedGetResponse.status_code, 200)
    #     self.assertContains(linkedGetResponse, self.guid2)

    def test_language_header_filter(self):
        param = {"limit":1, "object":{"objectType": "Activity", "id":"foogie"}}
        path = "%s?%s" % (reverse(views.statements), urllib.urlencode(param))        
        lang_get_response = self.client.get(path, Accept_Language="en-US", X_Experience_API_Version="0.95", Authorization=self.auth)

        self.assertEqual(lang_get_response.status_code, 200)
        resp_list = json.loads(lang_get_response.content)
        stmts = resp_list["statements"]
        self.assertEqual(len(stmts), 1)
        self.assertContains(lang_get_response, "en-US")
        self.assertNotContains(lang_get_response, "en-GB")

    # Sever activities are PUT, but should be 6 since two have same ID and auth
    def test_number_of_activities(self):
        acts = len(models.activity.objects.all())
        self.assertEqual(6, acts)

    def test_update_activity_wrong_auth(self):
        wrong_username = "tester2"
        wrong_email = "test2@tester.com"
        wrong_password = "test2"
        wrong_auth = "Basic %s" % base64.b64encode("%s:%s" % (wrong_username, wrong_password))
        form = {"username":wrong_username, "email":wrong_email,"password":wrong_password,
            "password2":wrong_password}
        response = self.client.post(reverse(views.register),form, X_Experience_API_Version="0.95")

        stmt = json.dumps({"verb":{"id":"verb/uri/attempted"},"actor":{"objectType":"Agent", "mbox":"r@r.com"},
            "object": {"objectType": "Activity", "id":"foogie",
            "definition": {"name": {"en-US":"testname3"},"description": {"en-US":"testdesc3"},
            "type": "cmi.interaction","interactionType": "fill-in","correctResponsesPattern": ["answer"],
            "extensions": {"key1": "value1", "key2": "value2","key3": "value3"}}}, 
            "result": {"score":{"scaled":.85}, "completion": True, "success": True, "response": "kicked",
            "duration": self.firstTime, "extensions":{"key1": "value1", "key2":"value2"}},
            "context":{"registration": self.cguid1, "contextActivities": {"other": {"id": "NewActivityID2"}},
            "revision": "food", "platform":"bard","language": "en-US", "extensions":{"ckey1": "cval1",
            "ckey2": "cval2"}}, "authority":{"objectType":"Agent","name":"auth","mbox":"auth@example.com"}})
        
        post_response = self.client.post(reverse(views.statements), stmt, content_type="application/json",
            Authorization=wrong_auth, X_Experience_API_Version="0.95")
        self.assertEqual(post_response.status_code, 403)
        self.assertEqual(post_response.content, "This ActivityID already exists, and you do not have" + 
                        " the correct authority to create or update it.")

    def test_update_activity_correct_auth(self):
        stmt = json.dumps({"verb": {"id":"verb/url/changed-act"},"actor":{"objectType":"Agent", "mbox":"l@l.com"},
            "object": {"objectType": "Activity", "id":"foogie",
            "definition": {"name": {"en-US":"testname3"},"description": {"en-US":"testdesc3"},
            "type": "cmi.interaction","interactionType": "fill-in","correctResponsesPattern": ["answer"],
            "extensions": {"key1": "value1", "key2": "value2","key3": "value3"}}}, 
            "result": {"score":{"scaled":.85}, "completion": True, "success": True, "response": "kicked",
            "duration": self.firstTime, "extensions":{"key1": "value1", "key2":"value2"}},
            "context":{"registration": self.cguid1, "contextActivities": {"other": {"id": "NewActivityID2"}},
            "revision": "food", "platform":"bard","language": "en-US", "extensions":{"ckey1": "cval1",
            "ckey2": "cval2"}}, "authority":{"objectType":"Agent","name":"auth","mbox":"auth@example.com"}})

        post_response = self.client.post(reverse(views.statements), stmt, content_type="application/json",
            Authorization=self.auth, X_Experience_API_Version="0.95")
        
        act = models.activity.objects.get(activity_id="foogie")
        act_def = models.activity_definition.objects.get(activity=act)

        name_set = act_def.name.all()
        desc_set = act_def.description.all()

        self.assertEqual(name_set[0].key, "en-GB")
        self.assertEqual(name_set[0].value, "altname")

        self.assertEqual(name_set[1].key, "en-US")
        self.assertEqual(name_set[1].value, "testname3")

        self.assertEqual(desc_set[0].key, "en-GB")
        self.assertEqual(desc_set[0].value, "altdesc")

        self.assertEqual(desc_set[1].key, "en-US")
        self.assertEqual(desc_set[1].value, "testdesc3")

    def test_cors_post_put(self):
        bdy = {"statementId": "postputID"}
        bdy["content"] = {"verb":{"id":"verb/url"}, "actor":{"objectType":"Agent", "mbox": "r@r.com"},
            "object": {"id":"test_cors_post_put"}}
        bdy["Authorization"] = self.auth
        bdy["Content-Type"] = "application/json"
        path = "%s?%s" % (reverse(views.statements), urllib.urlencode({"method":"PUT"}))
        response = self.client.post(path, bdy, content_type="application/x-www-form-urlencoded", X_Experience_API_Version="0.95")
        self.assertEqual(response.status_code, 204)

        act = models.activity.objects.get(activity_id="test_cors_post_put")
        self.assertEqual(act.activity_id, "test_cors_post_put")

        agent = models.agent.objects.get(mbox="test1@tester.com")
        self.assertEqual(agent.name, "tester1")
        self.assertEqual(agent.mbox, "test1@tester.com")

    def test_issue_put(self):
        stmt_id = "33f60b35-e1b2-4ddc-9c6f-7b3f65244430" 
        stmt = json.dumps({"verb":{"id":"verb/uri"},"object":{"id":"scorm.com/JsTetris_TCAPI","definition":{"type":"media",
            "name":{"en-US":"Js Tetris - Tin Can Prototype"},"description":{"en-US":"A game of tetris."}}},
            "context":{"contextActivities":{"grouping":{"id":"scorm.com/JsTetris_TCAPI"}},
            "registration":"6b1091be-2833-4886-b4a6-59e5e0b3c3f4"},
            "actor":{"mbox":"mailto:tom.creighton.ctr@adlnet.gov","name":"Tom Creighton"}})

        path = "%s?%s" % (reverse(views.statements), urllib.urlencode({"statementId":stmt_id}))
        put_stmt = self.client.put(path, stmt, content_type="application/json", Authorization=self.auth, X_Experience_API_Version="0.95")
        self.assertEqual(put_stmt.status_code, 204) 

    def test_post_with_group(self):
        ot = "Group"
        name = "the group ST"
        mbox = "mailto:the.groupST@example.com"
        members = [{"name":"agentA","mbox":"mailto:agentA@example.com"},
                    {"name":"agentB","mbox":"mailto:agentB@example.com"}]
        group = json.dumps({"objectType":ot, "name":name, "mbox":mbox,"member":members})

        stmt = json.dumps({"actor":group,"verb":{"id": "http://verb/uri/created", "display":{"en-US":"created"}},
            "object": {"id":"i.pity.the.fool"}})
        response = self.client.post(reverse(views.statements), stmt, content_type="application/json", Authorization=self.auth, X_Experience_API_Version="0.95")
        self.assertEqual(response.status_code, 200)
        g = models.group.objects.get(mbox="mailto:the.groupST@example.com")
        self.assertEquals(g.name, name)
        self.assertEquals(g.mbox, mbox)
        mems = g.member.values_list("name", flat=True)
        self.assertEquals(len(mems), 2)
        self.assertIn("agentA", mems)
        self.assertIn("agentB", mems)


    def test_issue_put_no_version_header(self):
        stmt_id = '33f60b35-e1b2-4ddc-9c6f-7b3f65244431'
        stmt = json.dumps({"verb":"completed","object":{"id":"scorm.com/JsTetris_TCAPI/level2",
            "definition":{"type":"media","name":{"en-US":"Js Tetris Level2"},
            "description":{"en-US":"Starting at 1, the higher the level, the harder the game."}}},
            "result":{"extensions":{"time":104,"apm":229,"lines":5},"score":{"raw":9911,"min":0}},
            "context":{"contextActivities":{"grouping":{"id":"scorm.com/JsTetris_TCAPI"}},
            "registration":"b7be7d9d-bfe2-4917-8ccd-41a0d18dd953"},
            "actor":{"name":["tom creighton"],"mbox":["mailto:tom@example.com"]}})

        path = '%s?%s' % (reverse(views.statements), urllib.urlencode({"statementId":stmt_id}))
        put_stmt = self.client.put(path, stmt, content_type="application/json", Authorization=self.auth)
        self.assertEqual(put_stmt.status_code, 400)

    def test_issue_put_wrong_version_header(self):
        stmt_id = '33f60b35-e1b2-4ddc-9c6f-7b3f65244432'
        stmt = json.dumps({"verb":"completed","object":{"id":"scorm.com/JsTetris_TCAPI/level2",
            "definition":{"type":"media","name":{"en-US":"Js Tetris Level2"},
            "description":{"en-US":"Starting at 1, the higher the level, the harder the game."}}},
            "result":{"extensions":{"time":104,"apm":229,"lines":5},"score":{"raw":9911,"min":0}},
            "context":{"contextActivities":{"grouping":{"id":"scorm.com/JsTetris_TCAPI"}},
            "registration":"b7be7d9d-bfe2-4917-8ccd-41a0d18dd953"},
            "actor":{"name":["tom creighton"],"mbox":["mailto:tom@example.com"]}})

        path = '%s?%s' % (reverse(views.statements), urllib.urlencode({"statementId":stmt_id}))
        put_stmt = self.client.put(path, stmt, content_type="application/json", Authorization=self.auth, X_Experience_API_Version="0.90")
        self.assertEqual(put_stmt.status_code, 400)


    # Use this test to make sure stmts are being returned correctly with all data
    # def test_all_fields_activity_as_object(self):
    #     nested_stmt = Statement.Statement(json.dumps({"actor":{"objectType":"Agent","mbox": "tincan@adlnet.gov"},
    #         "verb":{"id": "http://adlnet.gov/expapi/verbs/assess","display": {"en-US":"assessed"}},
    #         "object":{"id":"http://example.adlnet.gov/tincan/example/simplestatement"}}))
    #     nested_st_id = nested_stmt.statement.statement_id

    #     stmt_id = str(uuid.uuid4())
    #     path = "%s?%s" % (reverse(views.statements), urllib.urlencode({"statementId":stmt_id}))
        
    #     stmt = json.dumps({"actor":{"objectType":"Agent","name": "Lou Wolford","account":{"homePage":"http://example.com", "name":"uniqueName"}},
    #         "verb":{"id": "http://adlnet.gov/expapi/verbs/created","display": {"en-US":"created", "en-GB":"made"}},
    #         "object": {"objectType": "Activity", "id":"/my/Activity/URL",
    #         "definition": {"name": {"en-US":"actName", "en-GB": "anotherActName"},
    #         "description": {"en-US":"This is my activity description.", "en-GB": "This is another activity description."},
    #         "type": "http://adlnet.gov/expapi/activities/cmi.interaction",
    #         "interactionType": "choice",
    #         "correctResponsesPattern": ["golf", "tetris"],
    #         "choices":[{"id": "golf", "description": {"en-US":"Golf Example", "en-GB": "GOLF"}},
    #         {"id": "tetris","description":{"en-US": "Tetris Example", "en-GB": "TETRIS"}},
    #         {"id":"facebook", "description":{"en-US":"Facebook App", "en-GB": "FACEBOOK"}},
    #         {"id":"scrabble", "description": {"en-US": "Scrabble Example", "en-GB": "SCRABBLE"}}],
    #         "extensions": {"key1": "value1", "key2": "value2","key3": "value3"}}}, 
    #         "result": {"score":{"scaled":.85, "raw": 85, "min":0, "max":100}, "completion": True, "success": True, "response": "Well done",
    #         "duration": "P3Y6M4DT12H30M5S", "extensions":{"resultKey1": "resultValue1", "resultKey2":"resultValue2"}},
    #         "context":{"registration": str(uuid.uuid4()), "contextActivities": {"other": {"id": "http://example.adlnet.gov/tincan/example/test"},
    #         "grouping":{"id":"http://groupingID"} },
    #         "revision": "Spelling error in choices.", "platform":"Platform is web browser.","language": "en-US",
    #         "statement":{"objectType":"StatementRef", "id":str(nested_st_id)},
    #         "extensions":{"contextKey1": "contextVal1","contextKey2": "contextVal2"}},
    #         "timestamp":self.firstTime})
        
    #     put_stmt = self.client.put(path, stmt, content_type="application/json", Authorization=self.auth, X_Experience_API_Version="0.95")
    #     self.assertEqual(put_stmt.status_code, 204)

    #     param = {"statementId":stmt_id}
    #     path = "%s?%s" % (reverse(views.statements), urllib.urlencode(param))        
    #     get_response = self.client.get(path, X_Experience_API_Version="0.95")
    #     print get_response



    # Use this test to make sure stmts are being returned correctly with all data
    # def test_all_fields_agent_as_object(self):
    #     nested_stmt = Statement.Statement(json.dumps({"actor":{"objectType":"Agent","mbox": "tincan@adlnet.gov"},
    #         "verb":{"id": "http://adlnet.gov/expapi/verbs/assess","display": {"en-US":"assessed"}},
    #         "object":{"id":"http://example.adlnet.gov/tincan/example/simplestatement"}}))
    #     nested_st_id = nested_stmt.statement.statement_id

    #     stmt_id = str(uuid.uuid4())
    #     path = "%s?%s" % (reverse(views.statements), urllib.urlencode({"statementId":stmt_id}))
    #     msha = hashlib.sha1("tom@example.com").hexdigest()        
        
    #     stmt = json.dumps({"actor":{"objectType":"Agent","name": "Lou Wolford","account":{"homePage":"http://example.com", "name":"louUniqueName"}},
    #         "verb":{"id": "http://adlnet.gov/expapi/verbs/helped","display": {"en-US":"helped", "en-GB":"assisted"}},
    #         "object": {"objectType":"Agent","name": "Tom Creighton","mbox_sha1sum":msha}, 
    #         "result": {"score":{"scaled":.85, "raw": 85, "min":0, "max":100}, "completion": True, "success": True, "response": "Well done",
    #         "duration": "P3Y6M4DT12H30M5S", "extensions":{"resultKey1": "resultValue1", "resultKey2":"resultValue2"}},
    #         "context":{"registration": str(uuid.uuid4()), "contextActivities": {"other": {"id": "http://example.adlnet.gov/tincan/example/test"}},
    #         "revision": "Spelling error in choices.", "platform":"Platform is web browser.","language": "en-US",
    #         "statement":{"objectType":"StatementRef", "id":str(nested_st_id)},
    #         "extensions":{"contextKey1": "contextVal1","contextKey2": "contextVal2"}},
    #         "timestamp":self.firstTime})
        
    #     put_stmt = self.client.put(path, stmt, content_type="application/json", Authorization=self.auth, X_Experience_API_Version="0.95")
    #     self.assertEqual(put_stmt.status_code, 204)

    #     param = {"statementId":stmt_id}
    #     path = "%s?%s" % (reverse(views.statements), urllib.urlencode(param))        
    #     get_response = self.client.get(path, X_Experience_API_Version="0.95")
    #     print get_response


    # Use this test to make sure stmts are being returned correctly with all data
    # def test_all_fields_substatement_as_object(self):
    #     nested_stmt = Statement.Statement(json.dumps({"actor":{"objectType":"Agent","mbox": "tincannest@adlnet.gov"},
    #         "verb":{"id": "http://adlnet.gov/expapi/verbs/assess","display": {"en-US":"assessed", "en-GB":"graded"}},
    #         "object":{"id":"http://example.adlnet.gov/tincan/example/simplestatement"}}))
    #     nested_st_id = nested_stmt.statement.statement_id

    #     nested_sub_stmt = Statement.Statement(json.dumps({"actor":{"objectType":"Agent","mbox": "tincannestsub@adlnet.gov"},
    #         "verb":{"id": "http://adlnet.gov/expapi/verbs/verb","display": {"en-US":"verb", "en-GB":"altVerb"}},
    #         "object":{"id":"http://example.adlnet.gov/tincan/example/simplenestedsubstatement"}}))
    #     nested_sub_st_id = nested_stmt.statement.statement_id

    #     stmt_id = str(uuid.uuid4())
    #     path = "%s?%s" % (reverse(views.statements), urllib.urlencode({"statementId":stmt_id}))
    #     msha = hashlib.sha1("tom@example.com").hexdigest()        
        
    #     stmt = json.dumps({"actor":{"objectType":"Agent","name": "Lou Wolford","account":{"homePage":"http://example.com", "name":"louUniqueName"}},
    #         "verb":{"id": "http://adlnet.gov/expapi/verbs/said","display": {"en-US":"said", "en-GB":"talked"}},
    #         "object": {"objectType": "SubStatement", "actor":{"objectType":"Agent","name":"Tom Creighton","mbox": "tom@adlnet.gov"},
    #         "verb":{"id": "http://adlnet.gov/expapi/verbs/assess","display": {"en-US":"assessed", "en-GB": "Graded"}},
    #         "object":{"id":"http://example.adlnet.gov/tincan/example/simplestatement",'definition': {'name': {'en-US':'SubStatement name'},
    #         'description': {'en-US':'SubStatement description'},
    #         'type': 'cmi.interaction','interactionType': 'matching',
    #         'correctResponsesPattern': ['lou.3,tom.2,andy.1'],'source':[{'id': 'lou',
    #         'description': {'en-US':'Lou', 'it': 'Luigi'}},{'id': 'tom','description':{'en-US': 'Tom', 'it':'Tim'}},
    #         {'id':'andy', 'description':{'en-US':'Andy'}}],'target':[{'id':'1',
    #         'description':{'en-US': 'SCORM Engine'}},{'id':'2','description':{'en-US': 'Pure-sewage'}},
    #         {'id':'3', 'description':{'en-US': 'SCORM Cloud', 'en-CH': 'cloud'}}]}},
    #         "result": {"score":{"scaled":.50, "raw": 50, "min":1, "max":51}, "completion": True,
    #         "success": True, "response": "Poorly done",
    #         "duration": "P3Y6M4DT12H30M5S", "extensions":{"resultKey11": "resultValue11", "resultKey22":"resultValue22"}},
    #         "context":{"registration": str(uuid.uuid4()),
    #         "contextActivities": {"other": {"id": "http://example.adlnet.gov/tincan/example/test/nest"}},
    #         "revision": "Spelling error in target.", "platform":"Ipad.","language": "en-US",
    #         "statement":{"objectType":"StatementRef", "id":str(nested_sub_st_id)},
    #         "extensions":{"contextKey11": "contextVal11","contextKey22": "contextVal22"}}}, 
    #         "result": {"score":{"scaled":.85, "raw": 85, "min":0, "max":100}, "completion": True, "success": True, "response": "Well done",
    #         "duration": "P3Y6M4DT12H30M5S", "extensions":{"resultKey1": "resultValue1", "resultKey2":"resultValue2"}},
    #         "context":{"registration": str(uuid.uuid4()), "contextActivities": {"other": {"id": "http://example.adlnet.gov/tincan/example/test"}},
    #         "revision": "Spelling error in choices.", "platform":"Platform is web browser.","language": "en-US",
    #         "statement":{"objectType":"StatementRef", "id":str(nested_st_id)},
    #         "extensions":{"contextKey1": "contextVal1","contextKey2": "contextVal2"}},
    #         "timestamp":self.firstTime})
        
    #     put_stmt = self.client.put(path, stmt, content_type="application/json", Authorization=self.auth, X_Experience_API_Version="0.95")
    #     self.assertEqual(put_stmt.status_code, 204)

    #     param = {"statementId":stmt_id}
    #     path = "%s?%s" % (reverse(views.statements), urllib.urlencode(param))        
    #     get_response = self.client.get(path, X_Experience_API_Version="0.95")
    #     print get_response


    # def test_post_list_rollback(self):
    #     stmts = json.dumps([{"verb":{"id": "http://adlnet.gov/expapi/verbs/passed","display": {"en-US":"passed"}},
    #         "object": {"id":"test_list_post"}, "actor":{"objectType":"Agent", "mbox":"t@t.com"}},
    #         {"verb":{"id": "http://adlnet.gov/expapi/verbs/passed","display": {"en-US":"passed"}},
    #         "object": {"id":"test_list_post"}, "actor":{"objectType":"Agent", "mbox":"t@t.com"}}])
    #     response = self.client.post(reverse(views.statements), stmts,  content_type="application/json", Authorization=self.auth, X_Experience_API_Version="0.95")
    #     self.assertEqual(response.status_code, 200)
    #     pdb.set_trace()