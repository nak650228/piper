#!/usr/bin/env python
# -*- encoding: utf-8 -*-

import os
import boto3

from typing import Dict

accessID=アクセスキーを入力してください
secretKEY=シークレットキーを指定してください

def scan_dynamodb(table_name: str) -> Dict:
    """
    DynamoDB内のデータを全て取得
    """
    dynamodb = boto3.resource('dynamodb',
            region_name='ap-northeast-1',
            aws_access_key_id=accessID,
            aws_secret_access_key=secretKEY 
    )
    table = dynamodb.Table(table_name)
    scan_result: Dict = table.scan()
    return scan_result["Items"]


def put_dynamodb(table_name: str, put_item: Dict) -> None:
    """
    DynamoDBに1つitem追加
    """
    dynamodb = boto3.resource('dynamodb',
            region_name='ap-northeast-1',
            aws_access_key_id=accessID,
            aws_secret_access_key=secretKEY 
    )
    
    table = dynamodb.Table(table_name)
    table.put_item(Item=put_item)
    return None


def delete_dynamodb(key: str, value: str) -> None:
    """
    DynamoDBから情報を削除
    """
    dynamodb = boto3.resource('dynamodb',
            region_name='ap-northeast-1',
            aws_access_key_id=accessID,
            aws_secret_access_key=secretKEY 
            )
    table = dynamodb.Table(table_name)
    table.delete_item(Key={key: value})
    return None

