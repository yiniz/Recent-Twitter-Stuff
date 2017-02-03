import tweepy
from pymongo import MongoClient
import json
import os
import time
import sys 

CKEY = ''
CSECRET = ''
AKEY = ''
ASECRET = ''


client = MongoClient()
db = client.IDs

AUTH_KEYS = []

def authenticate(listWithAuthKeys):
	auth = tweepy.OAuthHandler(listWithAuthKeys[0], listWithAuthKeys[1])
	auth.set_access_token(listWithAuthKeys[2], listWithAuthKeys[3])
	AUTH_KEYS.append(tweepy.API(auth))

def initAuthKeys(keyCount):
	try:
		with open('config.json', 'r') as f:
			data = json.load(f)
			CKEY = data["auth" + str(keyCount)]["CKEY"]
			CSECRET = data["auth" + str(keyCount)]["CSecret"]
			AKEY = data["auth" + str(keyCount)]["AToken"]
			ASECRET = data["auth" + str(keyCount)]["ASecret"]
			key = [CKEY, CSECRET, AKEY, ASECRET]
			authenticate(key)
			initAuthKeys(keyCount + 1)
	except KeyError:
		print("Used all keys.")


def formatJson(id, followersList, following):
	user = {"TID" : id}
	user["followers"] = {}
	user["following"] = {}
	
	for i,value in enumerate(followersList):
		user["followers"][str(i)] = str(value)	
	for i, value in enumerate(following):
		user["following"][str(i)] = str(value)
	return user

def getUserFollowers(follower, api):
	
	followerIDS = []
	followingIDS = []
	dbCollectionName = "info_" + str(follower) 
	for page in tweepy.Cursor(api.followers_ids, id = follower).pages(1):
		followerIDS.extend(page)
		time.sleep(61)
	
	for page in tweepy.Cursor(api.followers_ids, id = follower).pages(1):
		followingIDS.extend(page)
		time.sleep(61)
	db[dbCollectionName].insert_one(formatJson(follower, followerIDS, followingIDS))

if __name__ == '__main__':
	
	lookupTerm = sys.argv[1]
	dbCollectionName = "info_" + lookupTerm
	initAuthKeys(0)
	#auth = tweepy.OAuthHandler(CKEY, CSECRET)
	#auth.set_access_token(AKEY, ASECRET)
	#api = tweepy.API(auth)
		

	#Get initial following/follower list of user entered. 
	followerIDS = []
	followingIDS = []
	for page in tweepy.Cursor(api.followers_ids, id=lookupTerm).pages(1):
		followerIDS.extend(page)
		time.sleep(61)

	for page in tweepy.Cursor(api.friends_ids, id=lookupTerm).pages(1):
		followingIDS.extend(page)
		time.sleep(61)
	
		
	db[dbCollectionName].insert_one(formatJson(lookupTerm, followerIDS, followingIDS))

	for follower in followerIDS:
		getUserFollowers(follower, AUTH_KEYS[0])
