# -*- coding: utf-8 -*-
from django.conf import settings
from alibabacloud_dypnsapi20170525.client import Client as DypnsapiClient
from alibabacloud_tea_openapi import models as open_api_models
from alibabacloud_dypnsapi20170525 import models as dypnsapi_models
from alibabacloud_tea_util import models as util_models

class SmsService:
    @staticmethod
    def create_client() -> DypnsapiClient:
        access_key_id = getattr(settings, 'ALIBABA_CLOUD_ACCESS_KEY_ID', '')
        access_key_secret = getattr(settings, 'ALIBABA_CLOUD_ACCESS_KEY_SECRET', '')
        config = open_api_models.Config(
            access_key_id=access_key_id,
            access_key_secret=access_key_secret,
            endpoint='dypnsapi.aliyuncs.com'
        )
        return DypnsapiClient(config)

    @staticmethod
    def _sanitize_error(error):
        msg = str(error)
        technical_keywords = ["HTTPSConnectionPool", "SSLError", "Max retries exceeded", "Connection refused"]
        for keyword in technical_keywords:
            if keyword in msg:
                return "短信服务连接异常，请稍后重试"
        return msg

    @staticmethod
    def send_code(phone_number, scene_type):
        template_map = {
            "register": "100001", "login": "100001", "reset_pwd": "100003",
            "modify_phone": "100002", "bind_new": "100004", "verify_old": "100005",
            "change_password": "100003"
        }
        client = SmsService.create_client()
        send_request = dypnsapi_models.SendSmsVerifyCodeRequest(
            sign_name='速通互联验证码',
            template_code=template_map.get(scene_type, "100001"),
            phone_number=phone_number,
            template_param='{"code":"##code##","min":"5"}',
            code_type=1, code_length=6, valid_time=300, interval=60
        )
        runtime = util_models.RuntimeOptions()
        try:
            resp = client.send_sms_verify_code_with_options(send_request, runtime)
            if resp and resp.body:
                return resp.body.to_map()
            return {"Code": "ERROR", "Message": "Empty response from SMS service"}
        except Exception as error:
            print(f"SMS Send Error: {str(error)}")
            if hasattr(error, 'data'):
                return error.data
            return {"Code": "ERROR", "Message": SmsService._sanitize_error(error)}

    @staticmethod
    def verify_code(phone_number, code):
        client = SmsService.create_client()
        check_request = dypnsapi_models.CheckSmsVerifyCodeRequest(
            phone_number=phone_number,
            verify_code=code
        )
        runtime = util_models.RuntimeOptions()
        try:
            resp = client.check_sms_verify_code_with_options(check_request, runtime)
            if resp and resp.body:
                return resp.body.to_map()
            return {"Code": "ERROR", "Message": "Empty response from SMS service"}
        except Exception as error:
            print(f"SMS Verify Error: {str(error)}")
            if hasattr(error, 'data'):
                return error.data
            return {"Code": "ERROR", "Message": SmsService._sanitize_error(error)}
