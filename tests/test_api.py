import pytest
import requests
import urllib3

from conftest import HOST_ADDRESS

def test_post_discussion(jwt_client_token):
    headers = {}
    headers["Authorization"] = f"Bearer {jwt_client_token}"
    # heading and text
    mlp_payload = {
        "heading": "update!",
        "text_content": "postgres database crashed % !@ 23 &&&"
        # ('heading': ('', 'update', 'application/text'),

    }
    body, content_type = urllib3.encode_multipart_formdata(mlp_payload)
    headers["Content-Type"] = content_type
    ret = requests.post(f"{HOST_ADDRESS}/backend/api/discussions",data=body, headers=headers)
    # print(ret.json())
    assert ret.status_code == 200
    assert ret.json()["heading"] == "update!"
    assert ret.json()["text_content"] == "postgres database crashed % !@ 23 &&&"
    assert ret.json()["image_present"] == False

    # heading only
    mlp_payload = {
        "heading": "update 2! &&&kkk",
    }
    body, content_type = urllib3.encode_multipart_formdata(mlp_payload)
    headers["Content-Type"] = content_type
    ret = requests.post(f"{HOST_ADDRESS}/backend/api/discussions",data=body, headers=headers)
    # print(ret.json())
    assert ret.status_code == 401

    # text only
    mlp_payload = {
        "text_content": "postgres database crashed $$$$$ )()()()()(11!!!6^^^^^~~~~~~```)"
    }
    body, content_type = urllib3.encode_multipart_formdata(mlp_payload)
    headers["Content-Type"] = content_type
    ret = requests.post(f"{HOST_ADDRESS}/backend/api/discussions",data=body, headers=headers)
    # print(ret.json())
    assert ret.status_code == 401
   
    # with image file
    image_path = "testfiles/F64YVYAW8AAEWO5.jpeg"
    mlp_payload = {
        "heading": "update 2! &&&kkk",
        "text_content": "postgres database crashed $$$$$ )()()()()(11!!!6^^^^^~~~~~~```)",
        "image_file": (image_path, image_path) # optional
    }
    body, content_type = urllib3.encode_multipart_formdata(mlp_payload)
    headers["Content-Type"] = content_type
    ret = requests.post(f"{HOST_ADDRESS}/backend/api/discussions",data=body, headers=headers)
    # print(ret.json())
    assert ret.status_code == 200
    assert ret.json()["image_present"] == True

    # without text
    image_path = "testfiles/F64YVYAW8AAEWO5.jpeg"
    mlp_payload = {
        "heading": "update 2! &&&kkk",
        "image_file": (image_path, image_path) # optional
    }
    body, content_type = urllib3.encode_multipart_formdata(mlp_payload)
    headers["Content-Type"] = content_type
    ret = requests.post(f"{HOST_ADDRESS}/backend/api/discussions",data=body, headers=headers)
    # print(ret.json())
    assert ret.status_code == 401

    
    # with tags
    image_path = "testfiles/F64YVYAW8AAEWO5.jpeg"
    mlp_payload = {
        "heading": "update 2! &&&kkk",
        "text_content": "postgres database crashed $$$$$ )()()()()(11!!!6^^^^^~~~~~~```)",
        "image_file": (image_path, image_path), # optional
        "tags": "cs, viral   , redis, cat  " # optional
    }
    body, content_type = urllib3.encode_multipart_formdata(mlp_payload)
    headers["Content-Type"] = content_type
    ret = requests.post(f"{HOST_ADDRESS}/backend/api/discussions",data=body, headers=headers)
    assert ret.status_code == 200
    assert ret.json()["image_present"] == True
    assert len(ret.json()["tags"]) == 4 