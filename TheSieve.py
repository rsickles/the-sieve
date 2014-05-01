from bs4 import BeautifulSoup
import requests
import webbrowser
import urllib
import urllib2
import feedparser
from urlparse import urlparse
from Tkinter import *
import string
import pickle
import tkMessageBox
import random
from tkFileDialog import askdirectory

class The_Sieve:

	def applicationWindow(self):
		#UI
		self.root.title("The Sieve Home")
		self.query = StringVar()
		Label(self.root, text="Add Website To Favorites").grid(row=1)
		self.websiteAdd = Entry(self.root,textvariable=self.query).grid(row=2)
		Button(self.root,text="Add Website",command=self.saveQuery).grid(row=3)
		self.root.bind('<Return>', self.saveQuery)
		Label(self.root, text="Favorite Websites: ").grid(row=4)
		self.listboxMain = Listbox(self.root,exportselection=0,width="40")
		self.listboxMain.grid(row=5)
		self.scrollbar = Scrollbar(self.root)
		# attach listbox to scrollbar
		self.listboxMain.config(yscrollcommand=self.scrollbar.set)
		self.scrollbar.config(command=self.listboxMain.yview)
		self.listboxMain.bind("<Double-Button-1>", self.OnDouble)
		Label(self.root, text="Double Click Favorite Website To Read Most Recent Articles!").grid(row=6)
		#will get list of recommended articles and choose random 5 and put in list, if an article is opened
		#to delete article from favorites
		Button(self.root,text="Delete From Favorites",command=self.deleteFromfavorites).grid(row=7)
		#it is deleted from list stored in file
		Button(self.root,text="What Should I Read?",command=self.showRecommendations).grid(row=8)
		Button(self.root,text="Logout",command=self.logout).grid(row=10)
		#hides screen initially
		self.root.withdraw()
		#data for recommendations
		#code for recommendations
		self.title = StringVar()
		self.link = StringVar()
		self.size = StringVar()
		self.title.set("No Data")
		self.link.set("No Data")
		self.size.set("No Data")

	def deleteFromfavorites(self):
		selection = self.listboxMain.curselection()
		value = selection[0]
		del self.fav_websites[int(value)]
		self.website_list()

	def isArticle(self,title):
		title = title.lower()
		title_words = title.split(" ")
		if(len(title_words)<=3):
			return False
		for word in title_words:
			if( (self.isNumber(word)) or (word[-1:] in [".","?",":","!",","]) or
				(word[-1:] in string.ascii_letters and word[-2:-1]=="'")
				or (self.isWord(word))):
				pass
			else:
				return False
		return True


	def createFeedDict(self,feed):
		d = feedparser.parse(feed)
		self.site_links = dict()
		self.site_links_downloadable = list()
		for post in d.entries:
			self.site_links[post.title] = post.link
		self.createDownloadLinkList(self.site_links)
		return self.site_links

	def RSSFeed(self,url):
		try:
			if("http://" in url):
				page = urllib2.urlopen(url)
			else:
				page = urllib2.urlopen("http://" + url)

			soup = BeautifulSoup(page)
			link = soup.find('link', type="application/rss+xml")
			feed = link['href']
			self.createFeedDict(feed)
		except:
			self.createFeedDict(url+"/feed")
		#hack for when RSSFEEDPARSER returns a failed authentication token
		if(len(self.site_links)==0):
			if(len(self.createFeedDict(url+"/feed"))==0):
				self.article_list(url)
			else:
				self.listboxArticles.delete(0, END)
				for key,value in self.site_links.iteritems():
					self.listboxArticles.insert(END,key)
		else:
			self.listboxArticles.delete(0, END)
			for key,value in self.site_links.iteritems():
				self.listboxArticles.insert(END,key)

	def isNumber(self,number):
		for char in xrange(len(number)):
			if(not(number[char] in string.digits)):
				return False
		return True

	#Recommendation Engine does not start processing
	#until during logout as to not interfere with reading
	#articles and app user experience
	def storeRecommendations(self):
		commanility_dictionary = self.recommendArticle()
		self.selectMostRevelantArticles(commanility_dictionary)

	def OnDoubleRec(self,event):
		widget = event.widget
		selection = widget.curselection()
		#deleted from recommened articles that you should read
		del self.articles_to_read[int(selection[0])]
		value = widget.get(selection[0])
		url = self.recList[value]
		webbrowser.open_new(url)
		#saves every article read
		self.articles_read.append(url)
		#starts recommendation processing
		#gets title words from article read and adds to dictionary of words
		self.getTitleWordsFromArticle(url)
		#searches through all links from article you select
		self.getInitalLinks(url,value)


	#find url of article to download
	def downloadArticlesRec(self):
		selection = self.recArticles.curselection()
		value = selection[0]
		url = self.rec_list_url_only[int(value)][0]
		url = self.setfullLinkHeader(url)
		r  = requests.get(url)
		data = r.text
		contents = BeautifulSoup(data)
		self.compileHTML(contents,self.rec_list_url_only[int(value)][1])

	def removeRecArticle(self):
		selection = self.recArticles.curselection()
		value = selection[0]
		del self.read_these_articles[int(value)]
		del self.articles_to_read[int(value)]
		self.showListofRecommends()


	def compileHTML(self,html,name):
		filename = name
		self.strToFile(html, filename )

	def strToFile(self,html,filename):
		location = askdirectory(title='Please Select Where To Save Article')
		filenameLoc = location + "/" + filename+".html"
		output = open(filenameLoc,"w")
		output.write(str(html))
		output.close()


	def showRecommendations(self):
		self.read_these_articles = list()
		self.rec_list_url_only = list()
		self.recList = dict()
		if(len(self.articles_to_read)>5):
			#pick random 5 of them
			articles_chosen = 0
			while articles_chosen<5:
				choice = random.randint(0,len(self.articles_to_read)-1)
				if(not(self.articles_to_read[choice] in self.read_these_articles)):
					self.read_these_articles.append(self.articles_to_read[choice])
					self.recList[self.articles_to_read[choice][1]]=self.articles_to_read[choice][0]
					self.rec_list_url_only.append((self.articles_to_read[choice][0],self.articles_to_read[choice][1]))
					articles_chosen+=1
			#put choices numbers in a list and when clicked you can open that index and then remove from articles read list
			#add to root listbox for now
			self.rec = Toplevel()
			self.rec.title("The Sieve Recommendations")
			Label(self.rec, text="The Sieve Recommends You Read The Websites/Articles Below").pack()
			self.recArticles = Listbox(self.rec,exportselection=0,width="40",relief=SUNKEN)
			self.recArticles.pack()
			self.scrollbarChildRec = Scrollbar(self.rec)
			self.scrollbarChildRec.pack(side=RIGHT,fill=Y)
			self.recArticles.config(yscrollcommand=self.scrollbarChildRec.set)
			self.scrollbarChildRec.config(command=self.recArticles.yview)
			#fills child window with articles
			#binds double clicking on article
			instruct2 = Label(self.rec, text="Double Click To Read")
			instruct2.pack()
			self.recArticles.bind("<Double-Button-1>", self.OnDoubleRec)
			Button(self.rec, text='Remove Article From Recommendations', command=self.removeRecArticle).pack()
			download = Button(self.rec, text='Download Article',command=self.downloadArticlesRec)
			download.pack()
			Button(self.rec, text='Close', command=self.rec.destroy).pack()
			self.showListofRecommends()
		else:
			#need to read more articles before recommendation process can begin
			tkMessageBox.showinfo("Welcome", "Not Enough Data To Recommend, Keep Reading Articles")

	def showListofRecommends(self):
		self.recArticles.delete(0, END)
		for value in self.read_these_articles:
			self.recArticles.insert(END,value[1])

	def selectMostRevelantArticles(self,commanility_dictionary):
		#sort dicitonary by highest commanlity to lowest
		common_articles_sorted =  commanility_dictionary.values()
		sorted(common_articles_sorted, key=lambda x: x[1])
		#pick top five
		picking_index = 0
		articles_picked = 0
		while(articles_picked<6
		 and picking_index<len(common_articles_sorted)):
			#adds title and url to articles to read
			url = common_articles_sorted[picking_index][0]
			title = common_articles_sorted[picking_index][2]
			#check to see if article recommended is not arleady in list
			if(self.checkforExistenceinList(self.articles_to_read,title,url) and len(title)>15
				and not(self.setfullLinkHeader(url) in self.articles_read)):
				#add title to articles to read
				self.articles_to_read.append([url,title])
				articles_picked+=1
				picking_index+=1
			else:
				picking_index+=1

	#removes the ability for articles to appear twice in recommendations list
	def checkforExistenceinList(self,list,titleCheck,urlCheck):
		for title in xrange(len(list)):
			if(titleCheck==list[title][1]):
				return False
		for url in xrange(len(list)):
			if(urlCheck==list[url][0]):
				return False
		return True

	def LoginScreen(self):
		Label(self.mainWindow,text="Log In To The Sieve", font=("Helvetica", 16)).grid(row=1)
		#Log in
		self.username = StringVar()
		self.passw = StringVar()
		Label(self.mainWindow,text="Username: ").grid(row=3,sticky=E)
		self.mainWindow.bind('<Return>', self.login)
		Entry(self.mainWindow,textvariable=self.username).grid(row=3,column=1)
		Label(self.mainWindow,text="Password: ").grid(row=4,sticky=E)
		Entry(self.mainWindow,textvariable=self.passw,show="*").grid(row=4,column=1)
		Button(self.mainWindow,text="Login",command=self.login).grid(row=5,column=1)
		Button(self.mainWindow,text="Create Account",command=self.showRegistration).grid(row=5)

	def registration(self):
		#REGISTRATION
		self.reg.title("The Sieve Registration")
		Label(self.reg,text="Register", font=("Helvetica", 16)).grid(row=0)
		self.usernameREG = StringVar()
		self.passwREG = StringVar()
		self.passwREGAgain = StringVar()
		self.reg.bind('<Return>', self.register)
		Label(self.reg,text="Username: ").grid(row=1,sticky=E)
		Entry(self.reg,textvariable=self.usernameREG).grid(row=1,column=1)
		Label(self.reg,text="Password: ").grid(row=2,sticky=E)
		Entry(self.reg,textvariable=self.passwREG,show="*").grid(row=2,column=1)
		Label(self.reg,text="Enter Password Again: ").grid(row=3,sticky=E)
		Entry(self.reg,textvariable=self.passwREGAgain,show="*").grid(row=3,column=1)
		Button(self.reg,text="Submit",command=self.register).grid(row=4,column=1)
		Button(self.reg,text="Back to Login",command=self.mainScreen).grid(row=4,column=0)
		self.reg.withdraw()

	def register(self,*event):
		username = self.usernameREG.get()
		password = hash(self.passwREG.get())
		passwordagain = hash(self.passwREGAgain.get())
		if(len(username)==0 or len(str(password))<=1 or len(str(passwordagain))<=1):
			tkMessageBox.showinfo("Welcome", "You Forgot To Fill Out A Field!")
		elif(passwordagain!=password):
			tkMessageBox.showinfo("Welcome", "Passwords Do Not Match")
		else:
			try:
				file = open(username + ".txt", "w")
				file.write(username + " " + str(password) + " ")
				file.close()
				#Creates New User Data Structures
				#creates list of favorite websites
				self.fav_websites = []
				#create list of read articles
				self.articles_read = []
				#holds common words found in titles of articles read
				self.read_articles_words = dict()
				#holds all recommended articles to read
				self.articles_to_read = list()
				#whether instructions should be shown or not
				self.showInstructions = True
				data_to_save = [self.fav_websites,self.articles_read,self.read_articles_words,self.articles_to_read,self.showInstructions]
				output = open(username + '.pkl', 'wb')
				pickle.dump(data_to_save, output)
				output.close()
				tkMessageBox.showinfo("Welcome", "Registration Successful")
				self.mainScreen()
			except:
				tkMessageBox.showinfo("Welcome", "Registration Failed")

	def login(self,*event):
		username = self.username.get()
		password = self.passw.get()
		if(len(username)==0 or len(str(password))==0):
			tkMessageBox.showinfo("Welcome", "Login Failed")
		else:
			try:
				file = open(username + '.txt', 'r')
				fileItems = file.read().split(" ")
				if(fileItems[1] == str(hash(password))):
					tkMessageBox.showinfo("Welcome", "Login Successful")
					self.loggedInUser.set(username)
					self.getUserDataFromFile()
					#creates welcome message for user
					welcomeMessage="Welcome " + self.loggedInUser.get() + " to the Sieve!"
					Label(self.root, text=welcomeMessage).grid(row=0)
					#show instructions if first time logging in
					if(self.showInstructions==True):
						self.instructions()
						#shows application window
					self.showApplication()
				else:
					tkMessageBox.showinfo("ERROR", "Password Invalid")
			except:
				 	tkMessageBox.showinfo("ERROR", "Username Invalid")

	def instructions(self):
		self.instruct = Toplevel()
		hello = "Greetings %s" % (self.loggedInUser.get())
		Label(self.instruct, text=hello).pack()
		self.showInstructions = False
		text = Text(self.instruct)
		instructions = """Welcome to the Sive\nPlease Add Your Websites To Your Favorites List \nDouble Click On Websites To Read Thier Most Recent Articles\nAfter An Article Opens,It May Show The Spinning Wheel.\nHowever Nothing Is Wrong And Just Wait Until It Finishes. :)\nYou Must Also Log Out For The Recommendations Engine To Finish Processing Data\nLet That Load Aswell :)"""
		text.insert(INSERT, instructions)
		text.pack()
		Button(self.instruct,text="Close Instructions",command=self.instruct.withdraw).pack()


	def showApplication(self):
		self.mainWindow.withdraw()
		self.root.deiconify()

	def showRegistration(self):
		self.mainWindow.withdraw()
		self.reg.deiconify()

	def mainScreen(self):
		self.reg.withdraw()
		self.mainWindow.deiconify()

	def logout(self):
		self.root.withdraw()
		self.saveData()
		tkMessageBox.showinfo("Welcome", "Logout Successful")
		self.mainWindow.deiconify()

	def saveData(self):
		#save information
		if(len(self.linkstoVisit)>0):
			self.findMoreLinks(len(self.linkstoVisit))
			self.storeRecommendations()
		data_to_save = [self.fav_websites,self.articles_read,self.read_articles_words,self.articles_to_read,self.showInstructions]
		output = open(self.loggedInUser.get() + '.pkl', 'wb')
		pickle.dump(data_to_save, output)
		output.close()

	def getUserDataFromFile(self):
		try:
			pkl_file = open(self.loggedInUser.get() + '.pkl', 'rb')
			data = pickle.load(pkl_file)
			pkl_file.close()
			self.fav_websites = data[0]
			self.articles_read = data[1]
			self.read_articles_words = data[2]
			self.articles_to_read = data[3]
			self.showInstructions = data[4]
			self.website_list()
		except:
			tkMessageBox.showinfo("ERROR", "Unable to Retrieve Your Data")

	def checkforInternet(self):
		try:
			requests.get("http://www.google.com")
		except:
			tkMessageBox.showinfo("ERROR", "You Need A Stable Internet Connection to Use This App")
			root.destroy()

	def __init__(self,mainWindow):
		self.checkforInternet()
		root.protocol('WM_DELETE_WINDOW', self.killBasic)
		self.loggedInUser = StringVar()
		self.loggedInUser.set("")
		self.fav = "No Data Available"
		#useless words not to scrape
		self.stopWords = [
		"a","an","and","are","as","at","be",
		"by","for","from","has","he",
		"in","is","it","its","of","on",
		"that","the","to","was","were","will","with"
		]
		self.recommendedArticleTitles = dict()
		self.linkstoVisit = list()
		#####SCREENS AND WINDOWS######
		#main window for login
		self.mainWindow = mainWindow
		self.LoginScreen()
		#application window
		self.root = Toplevel()
		self.root.protocol('WM_DELETE_WINDOW', self.killApplication)
		self.applicationWindow()
		#registration window
		self.reg = Toplevel()
		self.reg.protocol('WM_DELETE_WINDOW', self.killBasic)
		self.registration()
		#######END OF SCREENS AND WINDOWS#######

	def recommendArticle(self):
		#contains all read words
		readWords = self.read_articles_words
		#dictionary containing all recommended titles
		self.graphedTreeLinks = self.recommendedArticleTitles
		self.commanlityMatrix = dict()
		for (titles,url) in self.graphedTreeLinks.iteritems():
			wordArray = titles.split(" ")
			#begins to check each title word of found link with words of readWords
			wordSimilarityCount = 0
			for words in wordArray:
				if(words in readWords.keys() and not(words in self.stopWords)):
					wordSimilarityCount+=readWords[words]
			self.commanlityMatrix[titles] = [url,wordSimilarityCount,titles]
		return self.commanlityMatrix

	def getTitleWordsFromArticle(self,url):
		html = urllib.urlopen(url).read()
		soup = BeautifulSoup(html)
		paragraphs=soup.html.head.title.get_text().encode('utf-8').lower()
		localWords = paragraphs.split(" ")
   		for word in localWords:
   			if(not(word in self.stopWords) and self.isWord(word)):
   				if(word in self.read_articles_words):
   					self.read_articles_words[word]+=1
   				else:
   					self.read_articles_words[word] = 1

	def isWord(self,word):
		for char in xrange(len(word)):
			if(not(word[char] in string.ascii_letters)):
				return False
		return True


	def getInitalLinks(self,url,domainName):
		r  = requests.get(url)
		data = r.text
		soup = BeautifulSoup(data)
		for link in soup.findAll('a'):
			link_title = link.get_text().encode('utf-8')
			has_author = self.checkForAuthor(link,domainName)
			link_title = self.parseArticleTitle(link_title)
			if(len(link_title)>15 or has_author==True):
				#adds links to crawl upon loguout
				if(not(link.get('href') in self.linkstoVisit)):
					self.linkstoVisit.append(link.get('href'))

	#if article has an author then it must be an article
	#not an advertisement (advertisement reduction)
	def checkForAuthor(self,link,domainName):
		try:
			url = link.get('href')
			if(url[0] == "/"):
				newUrl = "http://" + domainName + url
			else:
				newUrl = url
			opener = urllib.urlopen(newUrl) #Open the URL Connection
			soup = BeautifulSoup(opener)
			soup = soup.get_text().encode('utf-8')
			return (("by" in soup) or ("By" in soup))
		except:
			return False

	def findMoreLinks(self,totalLength):
		indexOfList = 0
		growthFactor = 1
		while(len(self.linkstoVisit)<totalLength*growthFactor
			and indexOfList<len(self.linkstoVisit)):
			url = self.setfullLinkHeader(self.linkstoVisit[indexOfList])
			try:
				r  = requests.get(url)
				data = r.text
				soup = BeautifulSoup(data)
				for link in soup.findAll('a'):
					link_title = link.get_text().encode('utf-8')
					has_author = self.checkForAuthor(link,domainName)
					link_title = self.parseArticleTitle(link_title)
					if(len(link_title)>15 or has_author==True):
						if(not(link.get('href') in self.linkstoVisit)):
							self.linkstoVisit.append(link.get('href'))
				indexOfList+=1
			except:
				indexOfList+=1
		return self.navigateNewsLists()

	def navigateNewsLists(self):
		setLength = len(self.linkstoVisit)
		message = "Please Wait...%s Links Being Crawled For Comparison Data\nLet Wheel Spin :)" % (setLength)
		tkMessageBox.showinfo("Welcome", message)
		for link in xrange(setLength):
			try:
				html = urllib.urlopen(self.linkstoVisit[link]).read()
				soup = BeautifulSoup(html)
				title=soup.html.head.title.get_text().encode('utf-8').lower()
				if (not(title in self.recommendedArticleTitles.keys())):
					#also if link is not in articles read list
					if(not(self.setfullLinkHeader(self.linkstoVisit[link]) in self.articles_read)):
						self.recommendedArticleTitles[title] = self.linkstoVisit[link]
			except:
				pass
		#resets links to vist to zero to not recrawl links
		self.linkstoVisit = []


	def hasRSSFeed(self,url):
		if("http://" in url):
			page = urllib2.urlopen(url)
		else:
			page = urllib2.urlopen("http://" + url)
			url = "http://" + url
		soup = BeautifulSoup(page)
		if(soup.find('link', type="application/rss+xml")==None):
			try:
				urllib2.urlopen(url + "/feed")
				return True
			except:
				return None
		else:
			return True

	def OnDouble(self,event):
		widget = event.widget
		selection = widget.curselection()
		value = widget.get(selection[0])
		index = widget.curselection()[0]
		self.currentSite = index
		#gets value you click on and queries
		#only query for articles on link you click
		#creates childWindow
		self.child = Toplevel()
		instruct3 = Label(self.child, text="Articles To Read")
		instruct3.pack()
		self.listboxArticles = Listbox(self.child,exportselection=0,width="40",relief=SUNKEN)
		self.listboxArticles.pack()
		if(self.hasRSSFeed(value)==None):
			self.article_list(value)
		else:
			self.RSSFeed(value)
		self.scrollbarChild = Scrollbar(self.child)
		self.scrollbarChild.pack(side=RIGHT,fill=Y)
		self.listboxArticles.config(yscrollcommand=self.scrollbarChild.set)
		self.scrollbarChild.config(command=self.listboxArticles.yview)

		#fills child window with articles
		#binds double clicking on article
		self.listboxArticles.bind("<Double-Button-1>", self.OnDoubleArticles)
		instruct2 = Label(self.child, text="Double Click Article To Open")
		instruct2.pack()
		self.downloadButton = Button(self.child, text='Download Selected Articles',command=self.downloadArticles)
		self.downloadButton.pack()
		Button(self.child, text='Close Article List', command=self.child.destroy).pack()


	def downloadArticles(self):
		selection = self.listboxArticles.curselection()
		value = selection[0]
		url = self.site_links_downloadable[int(value)][1]
		url = self.setfullLinkHeader(url)
		r  = requests.get(url)
		data = r.text
		contents = BeautifulSoup(data)
		self.compileHTML(contents,self.site_links_downloadable[int(value)][0])


	def OnDoubleArticles(self,event):
		widget = event.widget
		selection = widget.curselection()
		value = widget.get(selection[0])
		url = self.site_links[value]
		url = self.setfullLinkHeader(url)
		webbrowser.open_new(url)
		#saves every article read
		self.articles_read.append(url)
		#starts recommendation processing
		#gets title words from article read and adds to dictionary of words
		self.getTitleWordsFromArticle(url)
		#searches through all links from article you select
		self.getInitalLinks(url,value)

	def setfullLinkHeader(self,url):
		domainName = self.fav_websites[int(self.currentSite)]
		parsedURL = urlparse(url).geturl().encode('utf-8')
		fixedLink = url
		if((domainName in parsedURL) == False and ("http://" in parsedURL)==False):
			if("http://" in domainName):
				header = domainName
			else:
				header = "http://" + domainName
			fixedLink = header + parsedURL
		return fixedLink

	def saveQuery(self,*event):
		text = self.query.get()
		#saves fav website into file and displays
		if(len(text)>0):
			if(not(text in self.fav_websites) and not(("www." + text) in self.fav_websites)
				and not(text.replace('www.','http://') in self.fav_websites)
				and not(("http://" + text) in self.fav_websites)
				and not(text.replace('http://','') in self.fav_websites)):
				try:
					if(not("http://" in text)):
						text = "http://" + text
						requests.get(text)
					else:
						requests.get(text)
					self.fav_websites.append(text)
				except:
					tkMessageBox.showinfo("ERROR", "URL Invalid")
			else:
				tkMessageBox.showinfo("ERROR", "Website Is Already A Favorite")
		else:
			tkMessageBox.showinfo("ERROR", "Please Enter In A URL :)")
		self.website_list()

	def article_list(self,text):
		self.create_site_article_lib(text)
		dict = self.site_links
		self.listboxArticles.delete(0, END)
		if(len(dict)==0):
			tkMessageBox.showinfo("ERROR", "No News Can Be Found For This Website")
			self.child.destroy()
		else:
			for key,value in dict.iteritems():
				self.listboxArticles.insert(END,key)

	def website_list(self):
		self.listboxMain.delete(0, END)
		for value in self.fav_websites:
			self.listboxMain.insert(END,value)


	#returns links of all most recent articles from site
	def create_site_article_lib(self,url):
		if("http://" in url):
			r  = requests.get(url)
		else:
			r  = requests.get("http://" + url)
		data = r.text
		soup = BeautifulSoup(data)
		#creates new list of articles
		self.site_links = dict()
		#creates list of links for download
		self.site_links_downloadable = list()
		#####
		for link in soup.find_all('a'):
			link_title = link.get_text().encode('utf-8')
			#basic decision making for article credibility
			if(self.isArticle(link_title)):
				self.site_links[link_title] = link.get('href')
		self.createDownloadLinkList(self.site_links)
		return

	def createDownloadLinkList(self,site_links):
		for key,value in site_links.iteritems():
			self.site_links_downloadable.append((key,value))


	#creates a article title parsed
	def parseArticleTitle(self,link_title):
		link_title = link_title.lower()
		newTitle = ""
		for char in xrange(len(link_title)):
			if(link_title[char] in string.ascii_letters or ord(link_title[char]) == 32):
				newTitle+=link_title[char]
		return newTitle

	def killBasic(self):
		if tkMessageBox.askokcancel("Quit", "Press 'Ok' To Exit The Sieve"):
			root.destroy()

	def killApplication(self):
		if tkMessageBox.askokcancel("Quit", "Press 'Ok' To Exit The Sieve"):
			#saves data to users file
			self.saveData()
			#then closes application
			root.destroy()

root = Tk()
app = The_Sieve(root)
root.title("The Sieve")
root.mainloop()


