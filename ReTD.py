import sys, os, re 
from os import path



from PyQt5.QtCore import QEventLoop, QDir, QUrl
import networkx as nx

import community as community_louvain
import matplotlib.cm as cm

from datetime import datetime, timedelta
import collections
from PyQt5.QtWidgets import QMainWindow, QPushButton, QWidget, QFrame,\
    QGridLayout, QTabWidget, QLabel, QLineEdit, QTreeView, QRadioButton,\
    QHBoxLayout, QSlider, QFileDialog, QTableView, QComboBox,\
    QRadioButton, QMessageBox, QSizePolicy, QApplication, QVBoxLayout,\
    QListWidget, QAbstractItemView, QAbstractScrollArea, QButtonGroup

    
from PyQt5.QtGui import QBrush, QColor 
from PyQt5.QtCore import QAbstractTableModel, Qt, QRect, QPoint

import pandas as pd
from wordcloud import WordCloud
import numpy as np

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties
from matplotlib.colors import ListedColormap

  
# Creating the main window 
class App(QMainWindow): 
    def __init__(self): 
        super().__init__() 
        self.title = 'ReTD Version 0.89'
        self.left = 50
        self.top = 50
        self.width = 800
        self.height = 600
        self.user_followers = {}
        self.textTweet = []
        self.all_data = ''
        self.main_data = ''
        self.list_of_dates = []
        self.list_of_30hashtags = {}
        self.list_of_30replies = {}
        self.list_of_30mentions = {}
        self.list_of_30RT = {}
        self.stopWords = []
        self.setWindowTitle(self.title) 
        self.setGeometry(self.left, self.top, self.width, self.height) 
  
        self.tab_widget = MyTabWidget(parent=self) 
        self.setCentralWidget(self.tab_widget) 
  
        self.show() 
  
# Creating tab widgets 
class MyTabWidget(QTabWidget): 
    def __init__(self, parent): 
        #super(QWidget, self).__init__(parent) 
        super(QTabWidget, self).__init__(parent)
        self.parent = parent
        self.layout = QVBoxLayout(self) 
        self.title = 'MyTabWidget'
  
        # Initialize tab screen 
        self.tabs = QTabWidget() 
        self.tabData = tabData(parent = self) 
        self.tabFrequency = tabAwanKata(parent = self)
        self.tabFrequency.setDisabled(True)
        self.tabs.resize(600, 400)
        self.tabCon = tabConnection(parent = self)
        self.tabCon.setDisabled(True)
        self.tabCon.setVisible(False)
        self.tabKata = tabKataDalamKonteks(parent = self)
        self.tabKata.setDisabled(True)
        
  
        # Add tabs 
        self.tabs.addTab(self.tabData, "Data") 
        self.tabs.addTab(self.tabFrequency, "Frequency")
        self.tabs.addTab(self.tabCon,"Connection")
        self.tabs.addTab(self.tabKata, "Keyword in Context")
        #self.tabs.tabBarClicked.connect(self.handle_tabbar_clicked)

  
        # Add tabs to widget 
        self.layout.addWidget(self.tabs) 
        self.setLayout(self.layout) 
        
        self.tabs.currentChanged.connect(self.onChange) #changed!
        
    def onChange(self,i): #changed!
        
        if i != 2:
            #self.tabCon.setVisible(False)
            self.tabs.setTabEnabled(2,False)
        
    #def handle_tabbar_clicked(self, index):
        #print(index)

        #print("x2:", index * 2)
        

#class listKategori(QListWidget):
    
        
class tabConnection(QTabWidget):
    def __init__(self, parent): 
        #super(QWidget, self).__init__(parent)
        super(QTabWidget, self).__init__(parent)
        
        self.parent = parent
        
        #To see if the data is user of hashtag
        self.type_of_data = ''
        
        
        self.figure = plt.figure()
        self.canvas = FigureCanvas(self.figure)
        self.canvas.setVisible(False)
        self.canvas.setParent(self)
        
        self.tblConnection = QTableView()
        self.tblConnection.setVisible(False)
        
        self.toolbar = NavigationToolbar(self.canvas, self)
        
        #self.list_of_accounts = {}
        self.dict_of_retweeting = {}
        self.dict_edges_retweeting = {}
        self.dict_of_replying = {}
        self.dict_edges_replying = {}
        self.dict_of_mentioning = {}
        self.dict_edges_mentioning = {}
        
        self.dict_of_retweeted = {}
        self.dict_edges_retweeted = {}
        self.dict_of_replied = {}
        self.dict_edges_replied = {}
        self.dict_of_mentioned = {}
        self.dict_edges_mentioned = {}
        
        self.dict_of_hashtag = {}
        self.dict_edges_hashtag = {}
        
        self.dict_of_tweet = {}
        self.dict_edges_tweet = {}
        
        self.msgBox = QMessageBox()
        self.glayout = QGridLayout()
        #self.graph_hlayout = QHBoxLayout() 
        
        self.lbUserHashtag = QLabel()
        
        self.lwUserHashtag = QListWidget()
        self.lwUserHashtag.setSelectionMode(
            QAbstractItemView.ExtendedSelection
        )
        
        self.btNetwork = QPushButton()
        self.btNetwork.setText('Network')
        self.btNetwork.clicked.connect(self.createNetwork)
        
        self.btTable = QPushButton()
        self.btTable.setText('Table')
        self.btTable.clicked.connect(self.createTableConnection)
        
        self.btAllTime = QPushButton()
        self.btAllTime.setText('Chart for All Time')
        self.btAllTime.clicked.connect(self.createPlotAllTime)
        
        #RadioButton User Criteria
        self.hbUserCriteria = QHBoxLayout()
        self.bgUserCriteria = QButtonGroup()
        self.frUserCriteria = QFrame()
        
        self.lbSharedCriteria = QLabel()
        self.lbSharedCriteria.setText("Shared")
        
        self.rbUserCriteriaRT = QRadioButton("Retweeting")
        self.rbUserCriteriaRT.toggled.connect(self.updateUserCriteriaScreen)
        #self.rbUserCriteriaRT.setChecked(True)
        self.userCriteria = 'Retweeting'
        
        self.rbUserCriteriaReply = QRadioButton("Replying")
        self.rbUserCriteriaReply.toggled.connect(self.updateUserCriteriaScreen)
        
        self.rbUserCriteriaMention = QRadioButton("Mentioning")
        self.rbUserCriteriaMention.toggled.connect(self.updateUserCriteriaScreen)
        
        self.rbUserCriteriaRTed = QRadioButton("Retweeted")
        self.rbUserCriteriaRTed.toggled.connect(self.updateUserCriteriaScreen)
        
        
        self.rbUserCriteriaReplied = QRadioButton("Replied")
        self.rbUserCriteriaReplied.toggled.connect(self.updateUserCriteriaScreen)
        
        self.rbUserCriteriaMentioned = QRadioButton("Mentioned")
        self.rbUserCriteriaMentioned.toggled.connect(self.updateUserCriteriaScreen)
        
        self.lbUserCriteria = QLabel()
        self.lbUserCriteria.setText("Users")
                
        #Put the above radio button into the button group
        self.bgUserCriteria.addButton(self.rbUserCriteriaRT)
        self.bgUserCriteria.addButton(self.rbUserCriteriaReply)
        self.bgUserCriteria.addButton(self.rbUserCriteriaMention)
        
        self.bgUserCriteria.addButton(self.rbUserCriteriaRTed)
        self.bgUserCriteria.addButton(self.rbUserCriteriaReplied)
        self.bgUserCriteria.addButton(self.rbUserCriteriaMentioned)
        
        
        self.hbUserCriteria.addWidget(self.lbSharedCriteria)
        
        self.hbUserCriteria.addWidget(self.rbUserCriteriaRT)
        self.hbUserCriteria.addWidget(self.rbUserCriteriaReply)
        self.hbUserCriteria.addWidget(self.rbUserCriteriaMention) 
        
        self.hbUserCriteria.addWidget(self.rbUserCriteriaRTed)
        self.hbUserCriteria.addWidget(self.rbUserCriteriaReplied)
        self.hbUserCriteria.addWidget(self.rbUserCriteriaMentioned)
        
                       
        self.hbUserCriteria.addWidget(self.lbUserCriteria)
        
        self.frUserCriteria.setLayout(self.hbUserCriteria)
        
        self.rbShowNumberConnection = QRadioButton('Show #Connection')
        self.rbShowNumberConnection.setAutoExclusive(False)
        
        self.btCreateWordCloud = QPushButton('WordCloud')
        self.btCreateWordCloud.clicked.connect(self.createTableWordCloud)
        self.btCreateWordCloud.setVisible(False)
        self.rbBackground = QRadioButton("Dark Background")
        self.rbBackground.setAutoExclusive(False)
        #self.rbBackground.setCheckable(True)
        self.rbBackground.setVisible(False)
        
        
        
        self.btSaveTableConnection = QPushButton()
        self.btSaveTableConnection.setText('Save Table')
        self.btSaveTableConnection.clicked.connect(self.saveTableConnection)
        self.btSaveTableConnection.setVisible(False)
        #Create Canvas
        
        
        self.lbJudul = QLabel()
        self.lbJudul.setAlignment(Qt.AlignCenter)
        
        #Save Graphml
        self.btSaveGraph = QPushButton()
        self.btSaveGraph.setText('Save Graph')
        self.btSaveGraph.clicked.connect(self.createSaveGraph)
        #self.btSaveGraph.setEnabled(False)
        self.btSaveGraph.setVisible(False)
        #Save Plot Time
        self.btDataTime = QPushButton()
        self.btDataTime.setText('Save Data')
        self.btDataTime.clicked.connect(self.saveDataTime)
        #self.btDataTime.setEnabled(False)
        self.btDataTime.setVisible(False)
        
        self.btSelectPartition = QPushButton()
        self.btSelectPartition.setText('Partition')
        self.btSelectPartition.clicked.connect(self.selectPartition)
        self.btSelectPartition.setVisible(False)
        
        
        
     
        #Row labels
        #self.glayout.addWidget(self.lbUserHashtag, 0, 0)
        self.glayout.addWidget(self.btNetwork, 0, 0)
        self.glayout.addWidget(self.btTable, 0, 1)
        self.glayout.addWidget(self.frUserCriteria, 0, 2, 1, 3)
        self.glayout.addWidget(self.btAllTime, 1, 0)
        
        self.glayout.addWidget(self.rbShowNumberConnection, 1, 1)
        self.glayout.addWidget(self.toolbar, 1, 2, 1, 3)
        self.glayout.addWidget(self.btSaveGraph, 1, 5)
        self.glayout.addWidget(self.btDataTime, 1, 5)
        self.glayout.addWidget(self.btSelectPartition, 1, 6)
        
        self.glayout.addWidget(self.lwUserHashtag, 2, 0, 3, 1)
        self.glayout.addWidget(self.btCreateWordCloud, 2, 1)
        self.glayout.addWidget(self.rbBackground, 2, 2)
        self.glayout.addWidget(self.btSaveTableConnection, 2, 3)
        
        self.glayout.addWidget(self.lbJudul, 3, 1, 1, 4)
        self.glayout.addWidget(self.canvas, 4, 1, 1, 6)
        self.glayout.addWidget(self.tblConnection, 3, 1, 2, 6)
        
        self.glayout.setRowStretch(4, 5)
        self.glayout.setColumnStretch(4,3)
 
        self.setLayout(self.glayout)
        
    
    def selectPartition(self):   
        if self.btSelectPartition.text() == 'Partition':
            itemsUserHashtag = [item.text() for item in self.lwUserHashtag.selectedItems()]
            
            if len(itemsUserHashtag) == 0:
                self.msgBox.setText("Select at least one item")
                self.msgBox.setWindowTitle("ReTD")
                self.msgBox.setStandardButtons(QMessageBox.Ok)
                self.msgBox.show()
                return
            
            selected_partition = []
            for item in itemsUserHashtag:
                if item in self.partition.keys():
                    selected_partition.append(self.partition[item])
                    
            if len(selected_partition) == 0:
                self.msgBox.setText("No selected item is part of the partition")
                self.msgBox.setWindowTitle("ReTD")
                self.msgBox.setStandardButtons(QMessageBox.Ok)
                self.msgBox.show()
                return
            
            for i in range(self.lwUserHashtag.count()):
                if self.lwUserHashtag.item(i).text() in self.partition.keys():
                    if self.partition[self.lwUserHashtag.item(i).text()] in selected_partition:
                        self.lwUserHashtag.item(i).setSelected(True)
            
            '''
            
            
            if not itemsUserHashtag[0] in self.partition.keys():
                
            
            selected_partition = self.partition[itemsUserHashtag[0]]
            for i in range(self.lwUserHashtag.count()):
                if self.lwUserHashtag.item(i).text() in self.partition.keys():
                    if self.partition[self.lwUserHashtag.item(i).text()] == selected_partition:
                        self.lwUserHashtag.item(i).setSelected(True)
                        #print(self.lwUserHashtag.item(i).text())
            '''
        else:
            selected_items = [item.text() for item in self.lwUserHashtag.selectedItems()]
            
            if len(selected_items) > 0:
                
                all_items = [self.lwUserHashtag.item(i).text() for i in range(self.lwUserHashtag.count())]
                remaining_items = [item for item in all_items if not item in selected_items]
                
                self.lwUserHashtag.clear()
                
                for item in remaining_items:    
                    self.lwUserHashtag.addItem(item)
                
        
        
            
    
    def saveDataTime(self):
        filename = QFileDialog.getSaveFileName(self, 'Save File', '', 'CSV file (*.csv)')
        savename = filename[0]
               
        if len(savename.strip()) == 0:
            self.msgBox.setText("There is no file to save!")
            self.msgBox.setWindowTitle("ReTD")
            self.msgBox.setStandardButtons(QMessageBox.Ok)
            self.msgBox.show()
            return
        
        self.df_time.to_csv(savename)
    
        
    
    def createSaveGraph(self):
        #filename = QFileDialog.getSaveFileName(self, 'Save File', '', 'graph files (*.graphml)')
        #savename = filename[0]
        
        filetypes = "GML (*.gml);;GRAPHML (*.graphml)"
        #filename = QFileDialog.getSaveFileName(self, 'Save File', '', 'graph files (*.graphml)')
        filename = QFileDialog.getSaveFileName(self, 'Save File', '', filetypes)
        savename = filename[0]
               
        if len(savename.strip()) == 0:
            self.msgBox.setText("There is no file to save!")
            self.msgBox.setWindowTitle("ReTD")
            self.msgBox.setStandardButtons(QMessageBox.Ok)
            self.msgBox.show()
            return
        
        #nx.write_graphml(self.G, savename,encoding='utf-8')
        
        if savename.endswith('graphml'):
            nx.write_graphml(self.G,savename)
        elif savename.endswith('gml'):
            nx.write_gml(self.G,savename)
    
        
        
    def turnPlot(self,on_off):
        if on_off == 'on':
            #print('Ini .......' + on_off)
            self.tblConnection.setVisible(False)
            self.btSaveTableConnection.setVisible(False)
            self.btCreateWordCloud.setVisible(False)
            self.rbBackground.setVisible(False)
            
               
            self.figure.clear()
            self.canvas.setVisible(True)
            self.lbJudul.setVisible(True)
            self.toolbar.setVisible(True)
            self.canvas.draw()
        else:
            #print(on_off)
            self.tblConnection.setVisible(True)
            self.btSaveTableConnection.setVisible(True)
            self.btCreateWordCloud.setVisible(True)
            self.rbBackground.setVisible(True)
            '''
            if self.type_of_data == 'User':
                self.frUserCriteria.setVisible(False)
            '''    
            self.canvas.setVisible(False)
            self.lbJudul.setVisible(False)
            self.toolbar.setVisible(False)

    
    def createTableWordCloud(self):
        self.btDataTime.setVisible(False)
        self.btSaveGraph.setVisible(False)
        
        self.rbShowNumberConnection.setVisible(False)
        #print('atas')
        self.turnPlot('on')
        #print('bawah')
        
        if self.rbBackground.isChecked():
            bg_color = 'black'
        else:
            bg_color = 'white'
        
        df = self.dfTable
        if len(df) == 0:
            return
        
        
        
        df['CleanedTweet'] = df['Tweet'].apply(lambda x: ' '.join([a.lower() \
                                               for a in x.split(' ') if (not (a.startswith('RT') or a.startswith('@') \
                                                                              or a.startswith('#')\
                                                                              or a.startswith('http'))) and a not in self.parent.parent.stopWords ]))\
            .apply(lambda x: re.sub(r'[^\w\s]', '', x))
            
        
        wordcloud = WordCloud(max_words = self.parent.tabFrequency.slJumlahKata.value(), \
                              stopwords = self.parent.parent.stopWords + self.parent.tabFrequency.leHapusKata.text().split(), background_color = bg_color).generate(' '.join(df['CleanedTweet'].to_list()))
        #print(len(self.parent.parent.stopWords))
        
        self.figure.clear()
        self.axes = self.figure.add_subplot()    
        #self.axes.set_title(self.tentukanJudul())
        #self.canvas.axes.clear()
        #self.canvas.axes.axis("off")
        self.axes.axis("off")
        #self.canvas.axes.imshow(wordcloud)
        self.axes.imshow(wordcloud)
        self.canvas.draw()
        
        
    
    def updateUserCriteriaScreen(self):
        self.btDataTime.setVisible(False)
        self.btSaveGraph.setVisible(False)
        
        self.figure.clear()
        self.canvas.draw()
        self.tblConnection.setVisible(False)
        
        
        self.userCriteria = self.sender().text().strip()
        
       
    def saveTableConnection(self):
        filename = QFileDialog.getSaveFileName(self, "Save Table as", "data.csv", "*.csv")
        savename = filename[0]
        if savename:
            self.dfTable.to_csv(savename)
        
        
    def createPlotAllTime(self):
              
        self.rbShowNumberConnection.setVisible(False)
        self.turnPlot('on')
        self.lbJudul.setVisible(False)
        #print('Create masuk plot')
        #def irisan(lst1, lst2):
        #    return list(set(lst1) & set(lst2))
        #Take selected
        df = self.parent.parent.all_data
        
        itemsUserHashtag = [item.text() for item in self.lwUserHashtag.selectedItems()]
        
        if self.type_of_data == 'User':
            #if self.userCriteria == 'Retweeted':
            if self.userCriteria == 'Retweeting':
                #df = df.loc[df['RT'].apply(lambda x: x in itemsUserHashtag)][['Date', 'RT', 'User']]
                df = df.loc[df['RT'].isin(itemsUserHashtag)][['Date', 'RT', 'User']]
                
                df_overtime = df.groupby(['Date','RT'])['User'].count().to_frame().reset_index()
                df_overtime = df_overtime.rename(columns = {'User': '#Retweeting Users'})
            #elif self.userCriteria == 'Replied':
            elif self.userCriteria == 'Replying':
                #df = df.loc[df['Reply'].apply(lambda x: x in itemsUserHashtag)][['Date', 'Reply', 'User']]
                df = df.loc[df['Reply'].isin(itemsUserHashtag)][['Date', 'Reply', 'User']]
                
                df_overtime = df.groupby(['Date','Reply'])['User'].count().to_frame().reset_index()
                df_overtime = df_overtime.rename(columns = {'User': '#Replying Users'})
            #if self.userCriteria == 'Mentioned':
            if self.userCriteria == 'Mentioning':
                #print('Banyaknya row sebelum mention dibersihkan ' + str(len(df)))
                #df =  df[df['Mention'] != []]
                df=df.loc[(df['Mention'].str.len() > 0),:]
                
                #print('banyaknya mention ' + str(len(df)))
                df = df.explode('Mention').reset_index(drop=True)
                #print('Sekarang banyaknya mention ' + str(len(df)))
                #df = df[df['Mention'].apply(lambda x: x in itemsUserHashtag)][['Date','User', 'Mention']]
                df = df[df['Mention'].isin(itemsUserHashtag)][['Date','User', 'Mention']]
                
                df_overtime = df.groupby(['Date','Mention'])['User'].count().to_frame().reset_index()
                df_overtime = df_overtime.rename(columns = {'User': '#Mentioning Users'})
                
            if self.userCriteria == 'Retweeted':
                df = df.loc[(df['User'].isin(itemsUserHashtag))][['Date','User', 'RT']]
                df['RT'].replace('', np.nan, inplace=True)
                df.dropna(subset=['RT'], inplace=True)
                df_overtime = df.groupby(['Date','User'])['RT'].count().to_frame().reset_index()
                df_overtime = df_overtime.rename(columns = {'RT': '#Retweeted Users'})
            if self.userCriteria == 'Replied':
                df = df.loc[df['User'].isin(itemsUserHashtag)][['Date','User', 'Reply']]
                df['Reply'].replace('', np.nan, inplace=True)
                df.dropna(subset=['Reply'], inplace=True)
                
                df_overtime = df.groupby(['Date','User'])['Reply'].count().to_frame().reset_index()
                df_overtime = df_overtime.rename(columns = {'Reply': '#Replied Users'})
            if self.userCriteria == 'Mentioned':
                df =  df.loc[df['Mention'].str.len()>0]
                df = df.explode('Mention').reset_index(drop=True)
                df = df[df['User'].isin(itemsUserHashtag)][['Date','User', 'Mention']]
                df_overtime = df.groupby(['Date','User'])['Mention'].count().to_frame().reset_index()
                df_overtime = df_overtime.rename(columns = {'Mention': '#Mentioned Users'})
            
        elif self.type_of_data == 'Hashtag':
            #df =  df.loc[df['Hashtag'] != []]
            df=df.loc[(df['Hashtag'].str.len() > 0),:]
            print('Banyaknya twit yang ada hashtag ' + str(len(df)))
            df = df.explode('Hashtag').reset_index(drop=True)
            print(df[['User','Hashtag']])
            df = df.loc[df['Hashtag'].apply(lambda x: x in itemsUserHashtag)][['Date','Hashtag','User']]
            df_overtime = df.groupby(['Date','Hashtag'])['User'].count().to_frame().reset_index()
            df_overtime = df_overtime.rename(columns = {'User': '#Tweeting Users'})
        
        elif self.type_of_data == 'Tweet':
            tweets = [self.parent.parent.dictTopTweets[item] for item in itemsUserHashtag]
            #to return tweet to tweet_frequency
            dict_tweet_to_tf = {}
            for idx, t in enumerate(tweets):
                dict_tweet_to_tf[t] = itemsUserHashtag[idx]
                
            
            #print(tweets)
            df = df.loc[df['Tweet'].isin(tweets)][['Date','Tweet','User']]
            df_overtime = df.groupby(['Date','Tweet'])['User'].count().to_frame().reset_index()
            df_overtime = df_overtime.rename(columns = {'User': '#Retweeting Users'})
            df_overtime['Tweet'] = df_overtime['Tweet'].apply(lambda x: dict_tweet_to_tf[x])
        #Tambahan
        from_date = df_overtime['Date'].min()
        to_date = df_overtime['Date'].max()
        d = timedelta(days = 2)
        from_date = from_date - d
        to_date = to_date + d
            
        idx = pd.date_range(from_date, to_date)
        #df_date.set_index('Date', inplace = True)
        #df_date = df_date.reindex(idx, fill_value=0)
        #Tambahan
        
        df_overtime.set_index('Date', inplace = True)
        #df_overtime = df_overtime.reindex(idx, fill_value=0)
        self.figure.clear()
        df_temp = df_overtime.groupby([df_overtime.index, df_overtime.columns[0]])[df_overtime.columns[-1]].first().unstack()
        df_temp = df_temp.reindex(idx, fill_value=0)
        
        self.axes = self.figure.subplots()
        
        df_temp.fillna(0).plot(ax = self.axes)
        
        self.df_time = df_temp
        
        #df_temp.plot(ax = self.axes)
        
        #self.axes.legend(itemsUserHashtag)
        
        if self.userCriteria.endswith('ed'):
            self.axes.set_title('The Number of Users ' + self.userCriteria + ' by these Accounts')
        else:
            self.axes.set_title('The Number of Users ' + self.userCriteria + ' these Accounts')
        self.canvas.draw()
        
        self.btDataTime.setVisible(True)
        self.btSaveGraph.setVisible(False)
        self.btSelectPartition.setVisible(False)
        
    
    def createTableConnection(self):
        self.btDataTime.setVisible(False)
        self.btSaveGraph.setVisible(False)
        self.btSelectPartition.setVisible(False)
        
        def irisan(lst1, lst2):
            return list(set(lst1) & set(lst2))
        
        self.rbShowNumberConnection.setVisible(False)
        self.turnPlot('off')
        
        itemsUserHashtag = [item.text() for item in self.lwUserHashtag.selectedItems()]
        #print(itemsUserHashtag)
               
            
        if len(itemsUserHashtag)<1:
            #If you select only one, then there is nothing to compare/connect
            self.msgBox.setText("Please select at least one item")
            self.msgBox.setWindowTitle("Warning")
            self.msgBox.setStandardButtons(QMessageBox.Ok)
            self.msgBox.show()
            return
        
        #Read all the data
        df = self.parent.parent.all_data
        
        #print('Coba ini adalah ' + self.userCriteria)
        if self.type_of_data == 'User':
            if self.userCriteria == 'Retweeting':
                df = df.loc[df['RT'].apply(lambda x: x in itemsUserHashtag)][['User','Tweet','RT']]
                df = df.groupby(['RT','Tweet'])['User'].count().to_frame().reset_index().sort_values('User', ascending=False)
                df = df.rename(columns = {'User': '#Retweeting Users'})
                self.dfTable = df[['#Retweeting Users','Tweet','RT']]        
            
            
            if self.userCriteria == 'Replying':
                df = df.loc[df['Reply'].apply(lambda x: x in itemsUserHashtag)][['User','Tweet','Reply','RT']]
                df.loc[df['RT'].str.strip() == '', 'RT'] = df['User']
                self.dfTable = df.groupby(['RT','Tweet','Reply'])['User'].count().to_frame().reset_index().sort_values('User', ascending=False)
                self.dfTable = self.dfTable.rename(columns = {'User':'#Retweeting Users', 'RT': 'Replying User', 'Reply':'Replied'})
                self.dfTable = self.dfTable[['Replying User', '#Retweeting Users', 'Tweet', 'Replied']]
                #print(self.dfTable.head())
            
            if self.userCriteria == 'Mentioning':
                df = df.loc[df['Mention'].apply(lambda x: len(irisan(x,itemsUserHashtag))>0)][['User','Tweet','Mention','RT']]
                df['Mention'] = df['Mention'].apply(lambda x: ' '.join(irisan(x,itemsUserHashtag)))
                df.loc[df['RT'].str.strip() == '', 'RT'] = df['User']
                self.dfTable = df.groupby(['RT','Tweet','Mention'])['User'].count().to_frame().reset_index().sort_values('User', ascending=False)
                self.dfTable = self.dfTable.rename(columns = {'User':'#Retweeting Users', 'RT': 'Mentioning User', 'Mention': 'Mentioned'})
                self.dfTable = self.dfTable[['Mentioning User', '#Retweeting Users', 'Tweet', 'Mentioned']]
                
            
            if self.userCriteria == 'Retweeted':
                #for item in itemsUserHashtag:
                #self.dfTable = df.loc[df['User'].apply(lambda x: x in itemsUserHashtag)][['User','Tweet','RT']][df['RT'] != ''].reset_index()
                #self.dfTable = df.loc[(df['User'].isin(itemsUserHashtag)) & (df['User'] != df['RT']) & (df['RT'] != '')][['User','Tweet','RT']].reset_index()
                self.dfTable = df.loc[(df['User'].isin(itemsUserHashtag)) & (df['RT'] != '') & (df['User'] != df['RT'])][['User','Tweet','RT']].reset_index()
                
                        
            if self.userCriteria == 'Replied':
                #for item in itemsUserHashtag:
                #self.dfTable = df.loc[(df['User'].apply(lambda x: x in itemsUserHashtag)) & (df['Reply'] != '') & (df['User'] != df['Reply'])][['User','Tweet','Reply']].reset_index()
                #print('UserCriteria ' + self.userCriteria)
                self.dfTable = df.loc[(df['User'].isin(itemsUserHashtag)) & (df['Reply'] != '') & (df['User'] != df['Reply'])][['User','Tweet','Reply']].reset_index()
                #self.dfTable = df.loc[(df['User'].isin(itemsUserHashtag)) & (df['Reply'] != '')][['User','Tweet','Reply']].reset_index()
                            
            if self.userCriteria == 'Mentioned':
                #for item in itemsUserHashtag:
                df = df.loc[df['User'].isin(itemsUserHashtag)]
                df = df.explode('Mention')
                df['Mention'].replace('', np.nan, inplace=True)
                df.dropna(subset=['Mention'], inplace=True)
                self.dfTable = df.loc[df['User'] != df['Mention']][['User','Tweet','Mention']]
                self.dfTable = self.dfTable.groupby(['User','Tweet'])['Mention'].apply(list).reset_index()
                #self.dfTable = df.loc[(df['User'].isin(itemsUserHashtag)) & (not df['User'] in df['Mention'])][['User','Tweet','Mention']][df['Mention'].apply(lambda x: x != [])].reset_index()
                
        elif self.type_of_data == 'Hashtag':
            df = df[df['Hashtag'].apply(lambda x: len(irisan(x,itemsUserHashtag))>0)][['User','Tweet','Hashtag','RT']].reset_index()
            df['Hashtag'] = df['Hashtag'].map(tuple)
            df = df.groupby(['Tweet','Hashtag','RT'])['User'].count().to_frame().reset_index().sort_values('User', ascending=False)
            df = df.rename(columns = {'User': '#Retweeting Users'})
            df['Hashtag'] = df['Hashtag'].map(list)
            self.dfTable = df[['#Retweeting Users','Tweet','Hashtag','RT']]     
        
        elif self.type_of_data == 'Tweet':
            lstFreq = [self.parent.tabFrequency.dataForGraph[item] for item in  itemsUserHashtag]
            lstRT = [item[:-len(str(self.parent.tabFrequency.dataForGraph[item]))] for item in itemsUserHashtag]
            tweets = [self.parent.parent.dictTopTweets[item] for item in itemsUserHashtag]
            
            self.dfTable = pd.DataFrame({'#Retweeting Users':lstFreq,
                                         'Tweet': tweets,
                                         'RT': lstRT})
            
            
            
        
        model = pandasModel(self.dfTable)
        #print(self.dfTable.columns)    
        
        self.tblConnection.setModel(model)
        
    
        
    def createNetwork(self):
        
        self.btSaveGraph.setEnabled(True)
        def flatten(lst):
            flst = []
            for subl in lst:
                for e in subl:
                    if not e in flst:
                        flst.append(e)
            return flst
        
        def irisan(lst1, lst2):
            return list(set(lst1) & set(lst2)) 
        
        def connection(A,B):
            bridge = {}
            for a in A:
                if not a in bridge.keys():
                    bridge[a] = min(A.count(a), B.count(a))
            return sum(bridge.values())
        
        self.rbShowNumberConnection.setVisible(True)
        self.turnPlot('on')
        
        #Collect the selections from List Widgets 
        itemsUserHashtag = [item.text() for item in self.lwUserHashtag.selectedItems()]
               
            
        if len(itemsUserHashtag)<2:
            #If you select only one, then there is nothing to compare/connect
            self.msgBox.setText("Please select more than one item")
            self.msgBox.setWindowTitle("Warning")
            self.msgBox.setStandardButtons(QMessageBox.Ok)
            self.msgBox.show()
            return
        
        #Read all the data
        df = self.parent.parent.all_data
        #print('Banyak data untuk digrafikkan ' + str(len(df)))
        #print('Di luar : Data yang diproses ' + self.type_of_data)
        
        if self.type_of_data == 'User':
            if self.userCriteria == 'Retweeting':
                for item in itemsUserHashtag:
                    if item not in self.dict_of_retweeting.keys():
                        #self.dict_of_retweeting[item] = df.loc[df['User'] == item.strip()]['RT'].drop_duplicates().tolist()
                        self.dict_of_retweeting[item] = list(filter(None, df.loc[df['RT'] == item.strip()]['User'].tolist()))
                itemsAll = self.dict_of_retweeting
                edges = self.dict_edges_retweeting
            if self.userCriteria == 'Replying':
                for item in itemsUserHashtag:
                    if item not in self.dict_of_replying.keys():
                        #self.dict_of_replying[item] = df.loc[df['User'] == item.strip()]['Reply'].drop_duplicates().tolist()
                        self.dict_of_replying[item] = list(filter(None,df.loc[df['Reply'] == item.strip()]['User'].tolist()))
                itemsAll = self.dict_of_replying
                edges = self.dict_edges_replying
            if self.userCriteria == 'Mentioning':
                for item in itemsUserHashtag:
                    if item not in self.dict_of_mentioning.keys():
                        #self.dict_of_mentioning[item] = list(filter(None,df.loc[df['Mention'].apply(lambda x: item in x)]['User'].explode('Mention').tolist()))
                        self.dict_of_mentioning[item] = list(filter(None,df.loc[df['Mention'].apply(lambda x: item in x)]['User'].tolist()))
                itemsAll = self.dict_of_mentioning
                edges = self.dict_edges_mentioning
            if self.userCriteria == 'Retweeted':
                for item in itemsUserHashtag:
                    if item not in self.dict_of_retweeted.keys():
                        #self.dict_of_retweeted[item] = df.loc[df['RT'] == item.strip()]['User'].drop_duplicates().tolist()
                        self.dict_of_retweeted[item] = list(filter(None,df.loc[df['User'] == item.strip()]['RT'].tolist()))
                itemsAll = self.dict_of_retweeted
                edges = self.dict_edges_retweeted
            if self.userCriteria == 'Replied':
                for item in itemsUserHashtag:
                    if item not in self.dict_of_replied.keys():
                        self.dict_of_replied[item] = list(filter(None,df.loc[df['User'] == item.strip()]['Reply'].tolist()))
                        #print('....Replied.....')
                        #print(self.dict_of_replied[item])
                itemsAll = self.dict_of_replied
                edges = self.dict_edges_replied
            if self.userCriteria == 'Mentioned':
                for item in itemsUserHashtag:
                    if item not in self.dict_of_mentioned.keys():
                        dfx = df.loc[df['User'] == item.strip()]
                        dfx = dfx.explode('Mention')
                        dfx['Mention'].replace('', np.nan, inplace=True)
                        dfx.dropna(subset=['Mention'], inplace=True)
                        
                        dfx = dfx.loc[dfx['User'] != dfx['Mention']]
                        
                        self.dict_of_mentioned[item] = list(filter(None,dfx['Mention'].tolist()))
                        #print('Account ' + item)
                        #print(self.dict_of_mentioned[item])
                itemsAll = self.dict_of_mentioned
                edges = self.dict_edges_mentioned
        
        elif self.type_of_data == 'Hashtag':
            #if data is hashtag
        
            for item in itemsUserHashtag:
                if item not in self.dict_of_hashtag.keys():
                    self.dict_of_hashtag[item] = list(filter(None,df[df['Hashtag'].apply(lambda x: item in x)]['User'].tolist()))
            itemsAll = self.dict_of_hashtag
            edges = self.dict_edges_hashtag
            
        elif self.type_of_data == 'Tweet':
            #tweets = [self.parent.parent.dictTopTweets[item] for item in itemsUserHashtag]
            
            for item in itemsUserHashtag:
                if item not in self.dict_of_tweet.keys():
                    self.dict_of_tweet[item] = list(filter(None,df[df['Tweet'] == self.parent.parent.dictTopTweets[item]]['User'].tolist()))
            itemsAll = self.dict_of_tweet
            edges = self.dict_edges_tweet
            
        #Store matrix in dictionary
        
        
        
            
            
        matrix_edges = []
        any_change = False
        for i in range(0, len(itemsUserHashtag)):
            #print('i = ' + itemsUserHashtag[i])
            for j in range(i+1, len(itemsUserHashtag)):
                #print('j = ' + itemsUserHashtag[j])
                if not itemsUserHashtag[i] in edges.keys():
                    edges[itemsUserHashtag[i]] = {}
                    number_connection = connection(itemsAll[itemsUserHashtag[i]],itemsAll[itemsUserHashtag[j]])
                    edges[itemsUserHashtag[i]][itemsUserHashtag[j]] = number_connection
                    any_change = True
                elif not itemsUserHashtag[j] in edges[itemsUserHashtag[i]].keys():
                    #edges[itemsUserHashtag[i]] = {}
                    number_connection = connection(itemsAll[itemsUserHashtag[i]],itemsAll[itemsUserHashtag[j]])
                    edges[itemsUserHashtag[i]][itemsUserHashtag[j]] = number_connection
                    any_change = True
                
                number_connection = edges[itemsUserHashtag[i]][itemsUserHashtag[j]]
                
                #number_connection = connection(itemsAll[itemsUserHashtag[i]],itemsAll[itemsUserHashtag[j]])
                
                #if self.matrix_All[itemsAll[i]][itemsAll[j]]>0:
                if number_connection > 0:
                    #g.add_edge(itemsAll[i],itemsAll[j])
                    matrix_edges.append((itemsUserHashtag[i],itemsUserHashtag[j], number_connection))
        
        
        #Store edges to related dictionary
        if any_change:
            #print('Berubah')
            if self.type_of_data == 'User':
                if self.userCriteria == 'Retweeting':
                    self.dict_edges_retweeting = edges
                if self.userCriteria == 'Replying':
                    self.dict_edges_replying = edges
                if self.userCriteria == 'Mentioning':
                    self.dict_edges_mentioning = edges
                if self.userCriteria == 'Retweeted':
                    self.dict_edges_retweeted = edges
                if self.userCriteria == 'Replied':
                    self.dict_edges_replied = edges
                if self.userCriteria == 'Mentioned':
                    self.dict_edges_mentioned = edges
            
            elif self.type_of_data == 'Hashtag':
                self.dict_edges_hashtag = edges
                
            elif self.type_of_data == 'Tweet':
                self.dict_edges_tweet = edges
        #else:
            #print('Nggak ada perubahan')
        
        
        
        
        
        
        if len(matrix_edges) == 0:
            #print('There is no shared ' + self.userCriteria + ' users among nodes')
            self.lbJudul.setText('There is no shared ' + self.userCriteria.lower() + ' users among nodes')
            return
        else:
            if self.userCriteria.endswith('ed'):
                self.lbJudul.setText('Each edge represents the number of users being ' + self.userCriteria.lower() + ' by the nodes')
            else:
                self.lbJudul.setText('Each edge represents the number of users ' + self.userCriteria.lower() + ' the nodes')
    
            
            
        #print(edges)
        G = nx.Graph()
        G.add_weighted_edges_from(matrix_edges)
        
        node_edges,edge_weights = zip(*nx.get_edge_attributes(G,'weight').items())
        edge_labels = {}
        for a,b,edge in matrix_edges:
            edge_labels[(a,b)] = edge
        
        
        
        partition = community_louvain.best_partition(G)
        self.partition = partition
        cmap = cm.get_cmap('viridis')
        col = 1/(max(partition.values()) + 1)
        color_map = []
        for node in G.nodes():
            color_map.append(cmap(partition[node]*col))
        
        number_of_partitions = len(set(partition.values()))
        #print('Banyaknya partition')
        #print(number_of_partitions)
        
        if number_of_partitions == 1:
            self.btSelectPartition.setText("Delete")
        else:
            self.btSelectPartition.setText("Partition")
        
        CustomCmap = ListedColormap(['yellow','green','blue'])
        pos = nx.spring_layout(G) 
        nx.draw(G, pos, node_color=color_map, with_labels=True, edgelist=node_edges, edge_color= edge_weights, width=2.0, edge_cmap = CustomCmap)
        #End of replace
        
        
        
        
        if self.rbShowNumberConnection.isChecked():
            nx.draw_networkx_edge_labels(G,pos,edge_labels=edge_labels, font_color='red')
        
        
        #Experiment to make labels of nodes displayed on Visone
        for node in G.nodes():
            G.nodes[node]['label'] = node
            
        
        
        
        self.G = G
        
        self.btDataTime.setVisible(False)
        self.btSaveGraph.setVisible(True)
        self.btSelectPartition.setVisible(True)
        
        
        self.canvas.draw_idle()
        self.canvas.setVisible(True)
    
        
        
class tabKataDalamKonteks(QTabWidget):
    def __init__(self, parent): 
        #super(QWidget, self).__init__(parent) 
        super(QTabWidget, self).__init__(parent)
        
        self.parent = parent
        
        self.df_hasil = pd.DataFrame()
        #Ada di baris pertama
        self.glayout = QGridLayout()
        
        self.btVisual = QPushButton('Visualization')
        self.btVisual.clicked.connect(self.visualizingData)
        
        self.lbCariKata = QLabel()
        self.lbCariKata.setText('Search')
        self.leCariKata = QLineEdit()
                
        self.lbCariKiri = QLabel('Left Words')
        #self.lbCariKiri.setVisible(False)
        self.leKataKiri = QLineEdit()
        #self.leKataKiri.setVisible(False)
        self.lbCariKanan = QLabel('Right Words')
        #self.lbCariKanan.setVisible(False)
        self.leKataKanan = QLineEdit()
        #self.leKataKanan.setVisible(False)
    
        self.lbSearch = QLabel('Search')
        self.btCariKataKotor = QPushButton()
        self.btCariKataKotor.setText('Original')
        self.btCariKataKotor.clicked.connect(lambda x: self.cariKataDiData('Tweet'))
        self.btCariKataBersih = QPushButton()
        self.btCariKataBersih.setText('Cleaned')
        self.btCariKataBersih.clicked.connect(lambda x: self.cariKataDiData('CuitBersih'))
        self.lbTweet = QLabel('Tweets')
        self.btHapusDuplikasi = QPushButton()
        self.btHapusDuplikasi.setText('Eliminate Duplications')
        self.btHapusDuplikasi.setEnabled(False)
        self.btHapusDuplikasi.clicked.connect(self.hapusDuplikasi)
        
        self.lbJumlahCuitan = QLabel()
        self.lbJumlahCuitan.setAlignment(Qt.AlignCenter)
        self.btSimpanKWIC = QPushButton()
        self.btSimpanKWIC.setText('Save') 
        self.btSimpanKWIC.clicked.connect(self.simpanKWIC)
        
        self.tblKataData = QTableView()
        #self.tblKataData.setMinimumHeight(1000)
        #self.tblKataData.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContents)
        #self.tblKataData.resizeColumnsToContents()
        
        
        self.glayout.addWidget(self.lbCariKata, 0, 0)
        self.glayout.addWidget(self.leCariKata, 0, 1)
        self.glayout.addWidget(self.lbCariKiri, 0, 2)
        self.glayout.addWidget(self.leKataKiri, 0, 3)
        self.glayout.addWidget(self.lbCariKanan, 0, 4)
        self.glayout.addWidget(self.leKataKanan, 0, 5)
        
        self.glayout.addWidget(self.lbSearch, 0, 6)
        self.glayout.addWidget(self.btCariKataKotor, 0, 7)
        self.glayout.addWidget(self.btCariKataBersih, 0, 8)
        self.glayout.addWidget(self.lbTweet, 0, 9)
        self.glayout.addWidget(self.btHapusDuplikasi, 0, 10)
        
        self.glayout.addWidget(self.btVisual, 1, 0, 1, 2)
        self.glayout.addWidget(self.lbJumlahCuitan, 1, 2, 1, 8)
        self.glayout.addWidget(self.btSimpanKWIC, 1, 10, 1, 2) 
        
        self.glayout.addWidget(self.tblKataData, 2, 0, 7, 12)
        
        self.setLayout(self.glayout)
        
    
    def visualizingData(self):
        #print("Masuk visualizing")
        
        self.parent.parent.all_data = self.df_hasil
        self.parent.tabFrequency.btMainData.setText("Back to Main Data")
        self.parent.tabFrequency.btMainData.setEnabled(True)
        #self.parent.tabFrequency.dataForGraph = {}
        #self.parent.tabFrequency.turnPlot("off")
        self.parent.tabFrequency.figure.clear()
        self.parent.tabFrequency.canvas.draw()
        self.parent.tabFrequency.tblCategory.setVisible(False)
        self.parent.tabFrequency.cbDariTanggal.setCurrentText(self.parent.parent.list_of_dates[0])
        self.parent.tabFrequency.cbDariTanggal.setEnabled(False)
        self.parent.tabFrequency.cbSampaiTanggal.setCurrentText(self.parent.parent.list_of_dates[-1])
        self.parent.tabFrequency.cbSampaiTanggal.setEnabled(False)
        
        #This is just to make the program check the data
        self.parent.tabFrequency.boolChangedDateDate = True
        
        
        self.parent.tabs.setCurrentIndex(1)
        self.parent.tabKata.setEnabled(False)
    
    
    def simpanKWIC(self):
        filename = QFileDialog.getSaveFileName(self, "Save Plot As", "data.csv", "*.csv")
        savename = filename[0]
        if savename:
            self.df_hasil.to_csv(savename)
        
    def hapusDuplikasi(self):
        #df = self.df_hasil.groupby(['Left','Keywords','Right']).size().to_frame()
        df = self.df_hasil.groupby(['Left','Keywords','Right','RT'])['User'].count().to_frame().reset_index()
        df = df.reset_index().sort_values('User', ascending = False)
        
        df.rename(columns = {'User':'#Users'}, inplace=True)
        df = df[['#Users','Left','Keywords','Right','RT']]
        #self.df_hasil = df
        #print(self.df_hasil.head(3))
        #self.df_hasil.sort_values(by=['Count'], ascending=False, inplace=True)
        
        
        #self.df_hasil.drop_duplicates(inplace=True)
        #model = pandasModelKWIC(self.df_hasil)
        model = pandasModelKWIC(df)
        self.tblKataData.setModel(model)
        self.btHapusDuplikasi.setEnabled(False)
        #self.lbJumlahCuitan.setText('Number of Tweets = ' + str(len(self.df_hasil)))
        self.lbJumlahCuitan.setText('Number of Tweets = ' + str(len(df)))
        
        
    def cariKataDiData(self, kolom):
        self.tblKataData.setVisible(True)
        cari_kata = self.leCariKata.text().split()
        if not cari_kata:
            return
        
        #df = self.parent.parent.all_data[kolom].to_frame()
        df = self.parent.parent.all_data
        #df = df[['User', kolom, 'RT']].copy()
        
        daftar_cari = '|'.join([ '(?<!\w)'+ kata.replace(r'*',r'\w*')+'(?!\w)' for kata in cari_kata])
        
        self.df_hasil = df.loc[df[kolom].str.contains(daftar_cari, regex=True, case=False)].copy()
        if len(self.df_hasil) == 0:
            self.pesanTiadaCuitan()            
            return

        self.df_hasil['Keywords'] = self.df_hasil[kolom].\
            apply(lambda x: re.search(daftar_cari, x, re.IGNORECASE)[0]).copy()
            
        self.df_hasil['Left'] = self.df_hasil.apply(lambda x: x[kolom][:x[kolom].find(x['Keywords'])], axis=1).copy()
        
        #self.df_hasil['Kanan'] = self.df_hasil.apply(lambda x: x.Tweet.split(x.Kata)[-1], axis=1)
        self.df_hasil['Right'] = self.df_hasil.apply(lambda x: x[kolom][x[kolom].find(x['Keywords'])+len(x['Keywords']):], axis=1).copy()
        
        
        
        cari_kata_kiri = self.leKataKiri.text().split()
        if cari_kata_kiri:
            daftar_cari = '|'.join([ '(?<!\w)'+ kata.replace(r'*',r'\w*')+'(?!\w)' for kata in cari_kata_kiri])
            #daftar_cari = '|'.join([kata.replace(r'*',r'\w*') for kata in cari_kata_kiri])
            self.df_hasil = self.df_hasil.loc[self.df_hasil.Left.str.contains(daftar_cari, regex=True, case=False)]
        
        if len(self.df_hasil) == 0:
            self.pesanTiadaCuitan() 
            return
                
        cari_kata_kanan = self.leKataKanan.text().split()
        if cari_kata_kanan:
            daftar_cari = '|'.join([ '(?<!\w)'+ kata.replace(r'*',r'\w*')+'(?!\w)' for kata in cari_kata_kanan])
            #daftar_cari = '|'.join([kata.replace(r'*',r'\w*') for kata in cari_kata_kanan])
            self.df_hasil = self.df_hasil.loc[self.df_hasil.Right.str.contains(daftar_cari, regex=True, case=False)]
        
        if len(self.df_hasil) == 0:
            self.pesanTiadaCuitan() 
            return
        
        df = self.df_hasil[['User','Left', 'Keywords','Right', 'RT']]
        
        #model = pandasModelKWIC(self.df_hasil)
        model = pandasModelKWIC(df)
        self.tblKataData.setModel(model)
        self.tblKataData.resizeColumnToContents(1)
        self.tblKataData.setColumnWidth(1,400)
        self.tblKataData.setColumnWidth(3,400)
        
        self.btHapusDuplikasi.setEnabled(True)
        
        self.lbJumlahCuitan.setText('Number of Tweets = ' + str(len(self.df_hasil)))
        
    def pesanTiadaCuitan(self):
        QMessageBox.about(self, "Warning", "There is no Tweet")
        self.tblKataData.setVisible(False)
        self.lbJumlahCuitan.setText('')
        
       

class MyLabel(QWidget):
    def __init__(self, parent=None):
        QWidget.__init__(self, parent=parent)
        self.p = QPixmap()

    def setPixmap(self, p):
        self.p = p
        self.update()

    def paintEvent(self, event):
        if not self.p.isNull():
            painter = QPainter(self)
            painter.setRenderHint(QPainter.SmoothPixmapTransform)
            painter.drawPixmap(self.rect(), self.p)


            

class tabAwanKata(QTabWidget):
    #Data will be processed due to:
    #(1) change of Date (we used boolean variable changeDate)
    #(2) change of category: self.dataForGraph will be emptied 
    #When the date and category are not changes, what need to be done is just different kind o visualization
    
    
    def __init__(self, parent): 
        #super(QWidget, self).__init__(parent) 
        super(QTabWidget, self).__init__(parent)
        self.parent = parent
        
        self.boolChangedDateDate = True
        self.dataForGraph = {}
        self.globalDataForGraph = {}
        
        self.btMainData = QPushButton("Main Data")
        self.btMainData.setEnabled(False)
        self.btMainData.clicked.connect(self.backToMainData)
        
        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)
        
        self.tblCategory = QTableView()
        self.tblCategory.setVisible(False)
        
        self.toolbar = NavigationToolbar(self.canvas, self)
        
        
        self.msgBox = QMessageBox()
        #Ada di baris pertama
        self.glayout = QGridLayout()
        self.btStopWords = QPushButton()
        self.btStopWords.setText('Select Stop Words')
        self.btStopWords.clicked.connect(self.unggahStopWords)
        
        self.lbHapusKata = QLabel()
        self.lbHapusKata.setText("Remove Words")
        self.leHapusKata = QLineEdit()
        self.leHapusKata.editingFinished.connect(self.editRemovedWords)
        
        self.minJumlahKata = 10
        self.maxJumlahKata = 40
        self.slJumlahKata =  QSlider(Qt.Horizontal,self)
        self.slJumlahKata.setRange(self.minJumlahKata,self.maxJumlahKata)
        self.slJumlahKata.setTickPosition(int((self.minJumlahKata + self.maxJumlahKata)/2))
        #self.slJumlahKata.setFocusPolicy(Qt.NoFocus)
        self.slJumlahKata.setPageStep(2)
        self.slJumlahKata.valueChanged[int].connect(self.nilaiJumlahKata)
        self.lbJumlahKata = QLabel()
        self.lbJumlahKata.setText(str(self.slJumlahKata.value()) + " Top Users")
        
              
        
        self.lbDariTanggal = QLabel()
        self.lbDariTanggal.setText("From")
        self.cbDariTanggal = QComboBox()
        self.cbDariTanggal.currentTextChanged.connect(self.changedDate)
        
        self.lbSampaiTanggal = QLabel()
        self.lbSampaiTanggal.setText("To")
        self.cbSampaiTanggal = QComboBox()
        self.cbSampaiTanggal.addItems(self.parent.parent.list_of_dates)
        self.cbSampaiTanggal.currentTextChanged.connect(self.changedDate)
                       
        self.lbKategori = QLabel()
        self.lbKategori.setText("Select")
        self.cbPilihKategori = QComboBox()
        #self.cbPilihKategori.addItems(['User','Tweet', 'Hashtag','Word','Emoji'])
        self.cbPilihKategori.addItems(['User','Tweet', 'Hashtag','Word'])
        self.cbPilihKategori.currentTextChanged.connect(self.ubahKonteksKategori)
        
        #RadioButton User Criteria
        self.userCriteriaText = ""
        self.userCriteria = ""
        self.hbUserCriteria = QHBoxLayout()
        self.bgUserCriteria = QButtonGroup()
        self.frUserCriteria = QFrame()
        #self.frUserCriteria = QtWidgets.QFrame()
        
        self.lbUserCriteria = QLabel()
        self.lbUserCriteria.setText("Most")
        
        self.rbUserCriteriaRT = QRadioButton("Retweeted")
        self.rbUserCriteriaRT.toggled.connect(self.updateUserCriteriaScreen)
        self.rbUserCriteriaRT.setChecked(True)
        self.userCriteria = 'RT'
        
        self.rbUserCriteriaReply = QRadioButton("Replied")
        self.rbUserCriteriaReply.toggled.connect(self.updateUserCriteriaScreen)
        
        self.rbUserCriteriaMention = QRadioButton("Mentioned")
        self.rbUserCriteriaMention.toggled.connect(self.updateUserCriteriaScreen)
        
        self.rbUserCriteriaFollowers = QRadioButton("Followers")
        self.rbUserCriteriaFollowers.toggled.connect(self.updateUserCriteriaScreen)
        
        self.rbUserCriteriaActive = QRadioButton("Active")
        self.rbUserCriteriaActive.toggled.connect(self.updateUserCriteriaScreen)
        
        #Put the above radio button into the button group
        self.bgUserCriteria.addButton(self.rbUserCriteriaRT)
        self.bgUserCriteria.addButton(self.rbUserCriteriaReply)
        self.bgUserCriteria.addButton(self.rbUserCriteriaMention)
        self.bgUserCriteria.addButton(self.rbUserCriteriaFollowers)
        self.bgUserCriteria.addButton(self.rbUserCriteriaActive)
        
        #Put the above radio button into the horizontal box layout
        self.hbUserCriteria.addWidget(self.lbUserCriteria)
        self.hbUserCriteria.addWidget(self.rbUserCriteriaRT)
        self.hbUserCriteria.addWidget(self.rbUserCriteriaReply)
        self.hbUserCriteria.addWidget(self.rbUserCriteriaMention)
        self.hbUserCriteria.addWidget(self.rbUserCriteriaFollowers)
        self.hbUserCriteria.addWidget(self.rbUserCriteriaActive)
        
        self.frUserCriteria.setLayout(self.hbUserCriteria)
        
        
        #Create set of buttons to display graph & save
        self.df_ToDisplay = pd.DataFrame()
        self.bgButtonDisplay = QButtonGroup()
        self.hbButtonDisplay = QHBoxLayout()
        self.frButtonDisplay = QFrame()  

        
        self.rbBackground = QRadioButton("Dark Background")
        #Drawing Cloud
        self.btBuatAwanKata = QPushButton()
        self.btBuatAwanKata.setText('Cloud')
        self.btBuatAwanKata.clicked.connect(self.buatAwan)
        #Drawing Bar Chart
        self.btBuatDiagram = QPushButton()
        self.btBuatDiagram.setText('Bar Chart')
        #self.btBuatDiagram.setVisible(False)
        self.btBuatDiagram.clicked.connect(self.buatDiagram)
        #Drawing Pie Chart
        self.btBuatPie = QPushButton()
        self.btBuatPie.setText('Pie Chart')
        self.btBuatPie.clicked.connect(self.buatPie)
        #self.btBuatPie.setVisible(False)
        #Creating Table
        #Drawing Pie Chart
        self.btBuatTable = QPushButton()
        self.btBuatTable.setText('Table')
        self.btBuatTable.clicked.connect(self.buatTable)
        #self.btBuatTable.setVisible(False)
        #Save Graph
        self.btSimpan = QPushButton()
        self.btSimpan.setText('Save')
        self.btSimpan.clicked.connect(self.saveCloudTable)
        self.btSimpan.setVisible(False)
        
        self.btConnect = QPushButton()
        self.btConnect.setText('Connection')
        self.btConnect.clicked.connect(self.gotoConnection)
        
        #Put in horizontal box
        self.hbButtonDisplay.addWidget(self.rbBackground)
        self.hbButtonDisplay.addWidget(self.btBuatAwanKata)
        self.hbButtonDisplay.addWidget(self.btBuatDiagram)
        self.hbButtonDisplay.addWidget(self.btBuatPie)
        self.hbButtonDisplay.addWidget(self.btBuatTable)
        self.hbButtonDisplay.addWidget(self.btConnect)
        self.hbButtonDisplay.addWidget(self.btSimpan)
        
        
        self.frButtonDisplay.setLayout(self.hbButtonDisplay)
        
        self.glayout.addWidget(self.btMainData, 0, 0, 1, 2)
        self.glayout.addWidget(self.btStopWords, 0, 2, 1, 2) 
        self.glayout.addWidget(self.lbHapusKata, 0, 4, 1, 2)
        self.glayout.addWidget(self.leHapusKata, 0, 6, 1, 2)
        
        
        self.glayout.addWidget(self.lbDariTanggal, 2, 0)
        self.glayout.addWidget(self.cbDariTanggal, 2, 1)
        self.glayout.addWidget(self.lbSampaiTanggal, 2, 2)
        self.glayout.addWidget(self.cbSampaiTanggal, 2, 3)
        self.glayout.addWidget(self.lbKategori, 2, 4)
        self.glayout.addWidget(self.cbPilihKategori, 2, 5)
        
        self.glayout.addWidget(self.frUserCriteria, 2, 6, 1, 4)
        #self.glayout.addWidget(self.frTweetCriteria, 2, 6, 1, 2)
        
        self.glayout.addWidget(self.frButtonDisplay,3,0,1,9)
        
        self.glayout.addWidget(self.toolbar,4,0,1,8)
        self.glayout.addWidget(self.slJumlahKata, 4, 8, 1, 3)
        self.glayout.addWidget(self.lbJumlahKata, 4, 11, 1, 3)
        
        self.glayout.addWidget(self.canvas,5,0, 1,11)
        #self.glayout.addWidget(self.tblCategory,4, 0, 2,11)
        self.glayout.addWidget(self.tblCategory,5, 0, 1,11)
        
        self.glayout.setRowStretch(5, 6)  
        
        self.setLayout(self.glayout)
        
    
    def editRemovedWords(self):
        self.figure.clear()
        self.canvas.draw()
        self.tblCategory.setVisible(False)
        self.dataForGraph = {}
    
    def backToMainData(self):
        self.parent.parent.all_data = self.parent.parent.main_data
        self.figure.clear()
        self.canvas.draw()
        self.tblCategory.setVisible(False)
        self.btMainData.setEnabled(False)
        self.dataForGraph = {}
        self.cbDariTanggal.setEnabled(True)
        self.cbSampaiTanggal.setEnabled(True)
        self.parent.tabKata.setEnabled(True)
        
    
    def changedDate(self):
        self.figure.clear()
        self.canvas.draw()
        self.tblCategory.setVisible(False)
        
        self.boolChangedDate = True
        self.df_ToDisplay = pd.DataFrame()
        self.dataForGraph = {}
        
        
    def ubahKonteksKategori(self,value):
        self.figure.clear()
        self.canvas.draw()
        self.tblCategory.setVisible(False)
        
        self.dataForGraph = {}
        if value == "User":
            self.frUserCriteria.show()
            self.lbJumlahKata.setText(str(self.slJumlahKata.value()) + " Top Users")
            
        
        else:
            self.frUserCriteria.hide()
            #self.frTweetCriteria.hide()
            if value == 'Tweet':
                self.lbJumlahKata.setText(str(self.slJumlahKata.value()) + " Top Tweets")
            elif value == 'Hashtag':
                self.lbJumlahKata.setText(str(self.slJumlahKata.value()) + " Top Hashtags")
            elif value == 'Word':
                self.lbJumlahKata.setText(str(self.slJumlahKata.value()) + " Top Words")
                
        '''
        if value == 'User' or value == 'Hashtag':
            self.btConnect.setVisible(True)
        else:
            self.btConnect.setVisible(False)
        '''
        
    def updateUserCriteriaScreen(self):
        self.figure.clear()
        self.canvas.draw()
        self.tblCategory.setVisible(False)
        
        self.dataForGraph = {}
        #temp_text = self.sender().text()
        self.userCriteriaText = self.sender().text()
        if self.userCriteriaText == 'Retweeted':
            self.userCriteria = 'RT'
            self.lbJumlahKata.setText(str(self.slJumlahKata.value()) + " Top Retweeted Users")
            
        elif self.userCriteriaText == 'Replied':
            self.userCriteria = 'Reply'
            self.lbJumlahKata.setText(str(self.slJumlahKata.value()) + " Top Replied Users")
            
        elif self.userCriteriaText == 'Mentioned':
            self.userCriteria = 'Mention'
            self.lbJumlahKata.setText(str(self.slJumlahKata.value()) + " Top Mentioned Users")
            
        elif self.userCriteriaText == 'Followers':
            self.userCriteria = 'Followers'
            self.lbJumlahKata.setText(str(self.slJumlahKata.value()) + " Users Having Most Followers")
            
        elif self.userCriteriaText == 'Active':
            self.userCriteria = 'Active'
            self.lbJumlahKata.setText(str(self.slJumlahKata.value()) + " Top Active Users")
            
            
        else:
            return 
    
    def gotoConnection(self):
        if self.dataForGraph:
            self.parent.tabCon.setEnabled(True)
            self.parent.tabCon.setVisible(True)
            self.parent.tabCon.lwUserHashtag.clear()
            self.parent.tabCon.lwUserHashtag.addItems(list(self.dataForGraph.keys()))
            
            #print('Inside goto ' + self.cbPilihKategori.currentText())
            
            if self.cbPilihKategori.currentText() == 'User': 
                self.parent.tabCon.type_of_data = 'User'
                self.parent.tabCon.frUserCriteria.setVisible(True)
                
                if self.userCriteria == 'RT':
                    self.parent.tabCon.rbUserCriteriaRT.setChecked(True)
                elif self.userCriteria == 'Reply':
                    self.parent.tabCon.rbUserCriteriaReply.setChecked(True)
                elif self.userCriteria == 'Mention':
                    self.parent.tabCon.rbUserCriteriaMention.setChecked(True)
                elif self.userCriteria == 'Followers':
                    self.parent.tabCon.rbUserCriteriaRT.setChecked(True)
                elif self.userCriteria == 'Active':
                    self.parent.tabCon.rbUserCriteriaRT.setChecked(True)
        
            elif self.cbPilihKategori.currentText() == 'Hashtag':
                self.parent.tabCon.type_of_data = 'Hashtag'
                self.parent.tabCon.frUserCriteria.setVisible(False) 
            
            elif self.cbPilihKategori.currentText() == 'Tweet':
                self.parent.tabCon.type_of_data = 'Tweet'
                self.parent.tabCon.frUserCriteria.setVisible(False) 
            
            self.parent.tabs.setCurrentIndex(2)
                
            self.parent.tabCon.figure.clear()
            self.parent.tabCon.canvas.draw()
            
        else:
            self.msgBox.setText("Please show the graph/table first")
            self.msgBox.setWindowTitle("Warning")
            self.msgBox.setStandardButtons(QMessageBox.Ok)
            self.msgBox.show()
            return
            
    
    
    def selectDataBasedOnDate(self):
        #Copy all date from the main program memory
        self.df_ToDisplay = self.parent.parent.all_data
        
        d1 = datetime.strptime(self.cbDariTanggal.currentText(),"%d/%m/%y")
        d2 = datetime.strptime(self.cbSampaiTanggal.currentText(),"%d/%m/%y")
        awal = min(d1,d2)
        akhir = max(d1,d2)
        if awal != akhir:
            mask = (self.df_ToDisplay['Date'] >= awal) & (self.df_ToDisplay['Date'] <= akhir)
            self.df_ToDisplay = self.df_ToDisplay.loc[mask]
        else:
            #mask = self.df['Date'] == awal
            self.df_ToDisplay = self.df_ToDisplay.loc[self.df_ToDisplay['Date'] == awal]
        
    
    def selectDataBasedOnCategory(self):
        def irisan(lst1, lst2):
            return list(set(lst1) & set(lst2)) 
        
        self.globalDataForGraph = {}
        
        pilihan = self.cbPilihKategori.currentText()
        
        number_all_rows = len(self.df_ToDisplay)
        
        if pilihan == 'Tweet':
            self.df_tweet_RT = self.df_ToDisplay.groupby(['Tweet','RT'])['User'].\
                count().to_frame().sort_values('User', ascending=False).reset_index().head(40)
            self.df_tweet_RT.columns = ['Tweet','Account','Frequency']
            accountFreq = (self.df_tweet_RT['Account']+self.df_tweet_RT['Frequency'].apply(lambda x: str(x))).tolist() 
            frequency = self.df_tweet_RT['Frequency'].tolist()
            tweets = self.df_tweet_RT['Tweet'].tolist()
            self.dataForGraph = dict(zip(accountFreq,frequency))
            self.parent.parent.dictTopTweets = dict(zip(accountFreq,tweets))
        else:
            if pilihan == 'User':
                
                if self.userCriteria == 'RT' or self.userCriteria == 'Reply':
                    df = self.df_ToDisplay.loc[self.df_ToDisplay[self.userCriteria].str.len() > 0]
                    
                    number_accounted_tweets = len(df)
                    
                    catCollection = ' '.join(df[self.userCriteria].tolist())
                
                elif self.userCriteria == 'Active': #Take 'User' 
                    #print(list(self.df_ToDisplay.columns))
                    catCollection = ' '.join(self.df_ToDisplay['User'].tolist())
                
                elif self.userCriteria == 'Mention':
                    df = self.df_ToDisplay.loc[self.df_ToDisplay[self.userCriteria].apply(lambda x: len(x)>0)]
                    number_accounted_tweets = len(df)
                    #catCollection = ' '.join(self.df_ToDisplay[self.userCriteria].apply(lambda x: ' '.join(x)).tolist())
                    print(list(df.columns))
                    catCollection = ' '.join(df.explode('Mention')['Mention'].tolist())
                elif self.userCriteria == 'Followers':
                    #Find the account with the highest number of followers who are active on the date
                    retweetedUsers = list(set(self.df_ToDisplay['RT'].tolist()))
                    repliedUsers = list(set(self.df_ToDisplay['Reply'].tolist()))
                    activeUsers = list(set(self.df_ToDisplay['User'].tolist()))
                    #mentionedUsers = self.df_ToDisplay['Mention'].tolist()
                    #mentionedUsers = [item for sublist in mentionedUsers for item in sublist]
                    #mentionedUsers = list(set(mentionedUsers))
                    mentionedUsers = self.df_ToDisplay.explode('Mention')['Mention'].tolist()
                    usersOfTheDay = list(set(retweetedUsers + repliedUsers + activeUsers + mentionedUsers))
                    
                    
                #We do not need to compute Followers it is already in self.user_followers
        
            elif pilihan == 'Hashtag':
                df = self.df_ToDisplay[self.df_ToDisplay[pilihan].apply(lambda x: len(x)>0)]
                number_accounted_tweets = len(df)
                catCollection = ' '.join(self.df_ToDisplay[pilihan].apply(lambda x: ' '.join(x)).tolist())
                                         
            elif pilihan == 'Word':
                catCollection = ' '.join(self.df_ToDisplay['CuitBersih'].tolist())
                mystopwords = self.parent.parent.stopWords
                removed_words = mystopwords + self.leHapusKata.text().split()
                #print('Jumlah removed words ' + str(len(removed_words)))
                if removed_words:
                    #print('Masuk removed .....?')
                    #print(self.leHapusKata.text().split())
                    catCollection = ' '.join([word for word in catCollection.split() if word not in removed_words])
               
            
                
            else:
                return
            
            if self.userCriteria != 'Followers': 
                counts = collections.Counter(catCollection.split())
                self.dataForGraph = dict(counts.most_common(40))
                number_of_top = self.slJumlahKata.value()
                
                
                if pilihan == 'User' and (self.userCriteria == 'RT' or self.userCriteria == 'Reply'):
                    list_values_of_dataForGraph = list(self.dataForGraph.values())
                    
                    if number_of_top < len(list_values_of_dataForGraph):
                        total_top = sum(list_values_of_dataForGraph[:number_of_top])
                    else:
                        total_top = sum(list_values_of_dataForGraph)
                    '''    
                    self.globalDataForGraph['Non-' + self.userCriteria + '\nTweets'] =  number_all_rows - number_accounted_tweets
                    self.globalDataForGraph['Other ' + self.userCriteria + '\nTweets'] = number_accounted_tweets - total_top
                    self.globalDataForGraph['Top ' + str(number_of_top) + ' ' + self.userCriteria + '\nTweets'] = total_top
                    '''
                    self.globalDataForGraph['Non-' + self.userCriteria + '\nTweets'] =  number_all_rows - number_accounted_tweets
                    self.globalDataForGraph['Other ' + self.userCriteria + '\nTweets'] = number_accounted_tweets - total_top
                    
                    if self.userCriteria == 'RT':
                        self.globalDataForGraph[self.userCriteria + ' Tweets\n' + 'from Top ' + str(number_of_top) + ' Users'] = total_top
                    #elif self.userCriteria == 'Reply':
                    else:
                        self.globalDataForGraph[self.userCriteria + ' Tweets\n' + 'to Top ' + str(number_of_top) + ' Users'] = total_top
                    
                    
                    
                elif pilihan == 'User' and self.userCriteria == 'Active':
                    list_values_of_dataForGraph = list(self.dataForGraph.values())
                    
                    if number_of_top < len(list_values_of_dataForGraph):
                        total_top = sum(list_values_of_dataForGraph[:number_of_top])
                    else:
                        total_top = sum(list_values_of_dataForGraph)
                        
                    #self.globalDataForGraph['Non-' + self.userCriteria + '\nTweets'] =  number_all_rows - number_accounted_tweets
                    self.globalDataForGraph['Other Tweets'] = number_all_rows - total_top
                    self.globalDataForGraph['Top ' + str(number_of_top) + ' ' + self.userCriteria + '\nTweets'] = total_top
                    
                    
                elif pilihan == 'User' and self.userCriteria == 'Mention':
                    dict_of_mentioned_accounts = list(self.dataForGraph.keys())
                    if number_of_top < len(dict_of_mentioned_accounts):
                        dict_of_mentioned_accounts = dict_of_mentioned_accounts[:number_of_top]
                    
                    df = df[df['Mention'].apply(lambda x: len(irisan(x, dict_of_mentioned_accounts))>0)]
                    total_top = len(df)
                    self.globalDataForGraph['Non-' + self.userCriteria + '\nTweets'] =  number_all_rows - number_accounted_tweets
                    self.globalDataForGraph['Other ' + self.userCriteria + '\nTweets'] = number_accounted_tweets - total_top
                    #self.globalDataForGraph['Top ' + str(number_of_top) + ' ' + self.userCriteria + '\nTweets'] = total_top
                    self.globalDataForGraph['Tweets Mentioning\n' + 'Top ' + str(number_of_top) + ' Users'] = total_top
                
                elif pilihan == 'Hashtag':
                    list_of_hashtags = list(self.dataForGraph.keys())
                    if number_of_top < len(list_of_hashtags):
                        list_of_hashtags = list_of_hashtags[:number_of_top]
                    
                    df = df[df['Hashtag'].apply(lambda x: len(irisan(x, list_of_hashtags))>0)]
                    total_top = len(df)
                    self.globalDataForGraph['Non-Hashtag\nTweets'] =  number_all_rows - number_accounted_tweets
                    self.globalDataForGraph['Other Hashtag\nTweets'] = number_accounted_tweets - total_top
                    self.globalDataForGraph['Top ' + str(number_of_top) + ' Hashtag\nTweets'] = total_top
            else:
                followersOfTheDay = []
                for user in usersOfTheDay: 
                    if user in self.parent.parent.user_followers.keys():
                        followersOfTheDay.append((user,self.parent.parent.user_followers[user]))
                #usersNumberOfFollowers = list(zip(usersOfTheDay,followersOfTheDay))
                dfUF = pd.DataFrame(followersOfTheDay, columns = ['User','Followers']).sort_values('Followers', ascending = False)
                self.dataForGraph = dict(zip(dfUF['User'].tolist(),dfUF['Followers'].tolist()))
         

    def saveCloudTable(self):
        filename = QFileDialog.getSaveFileName(self, "Save Table as", "data.csv", "*.csv")
        savename = filename[0]
        if savename:
            self.dfTableContent.to_csv(savename)
        
    def tentukanJudul(self):
        d1 = datetime.strptime(self.cbDariTanggal.currentText(),"%d/%m/%y")
        d2 = datetime.strptime(self.cbSampaiTanggal.currentText(),"%d/%m/%y")
        awal = min(d1,d2).strftime('%d-%m-%Y')
        akhir = max(d1,d2).strftime('%d-%m-%Y')
        
        pilihan = self.cbPilihKategori.currentText()
        
        if pilihan == 'User':
            judul = "Top " + str(self.slJumlahKata.value()) + " Most " + self.userCriteriaText + " Users"
        else:
            judul = "Top " + str(self.slJumlahKata.value()) + " " + pilihan
            
        if awal == akhir:
            judul = judul + " on " + str(awal)
        else:
            judul = judul + " from " + str(awal) + " to " + str(akhir)
        
        numberOfTweets = len(self.df_ToDisplay)
        judul = judul + " (" + str(numberOfTweets) + ")"
        return judul
        
        
    def buatAwan(self):
        self.canvas.setVisible(True)
        self.toolbar.setVisible(True)
        self.tblCategory.setVisible(False)
        self.btSimpan.setVisible(False)
        
        self.figure.clear()
        self.axes = self.figure.add_subplot()    
        
        #Select data if date 
        if self.boolChangedDateDate:
            self.selectDataBasedOnDate()
            self.selectDataBasedOnCategory()
        #Fill in self.dataForGraph if it was emptied
        if not self.dataForGraph:
            #print(self.dataForGraph)
            self.selectDataBasedOnCategory()
            
        if self.rbBackground.isChecked():
            bg_color = 'black'
        else:
            bg_color = 'white'
            
        if not self.dataForGraph:
            self.msgBox.setText("There is no tweet")
            self.msgBox.setWindowTitle("Warning")
            self.msgBox.setStandardButtons(QMessageBox.Ok)
            self.msgBox.show()
            return
        
        else:
            #print(self.dataForGraph)
            wordcloud = WordCloud(width=600, height=400, max_font_size=110, background_color = bg_color, max_words=self.slJumlahKata.value())\
               .generate_from_frequencies(self.dataForGraph) 
           
                
        self.axes.set_title(self.tentukanJudul())
        self.axes.axis("off")
        
        self.axes.imshow(wordcloud)
        self.canvas.draw()
        
                
    def buatDiagram(self):
        self.canvas.setVisible(True)
        self.toolbar.setVisible(True)
        self.tblCategory.setVisible(False)
        self.btSimpan.setVisible(False)
        
        
        #Select data if date 
        if self.boolChangedDateDate:
            self.selectDataBasedOnDate()
        #Fill in self.dataForGraph if it was emptied
        if not self.dataForGraph:
            self.selectDataBasedOnCategory()
       
        self.figure.clear()
        self.axes = self.figure.add_subplot()  
        self.axes.bar(list(self.dataForGraph.keys())[:self.slJumlahKata.value()], list(self.dataForGraph.values())[:self.slJumlahKata.value()])
        #plt.xticks(rotation = 45)
        self.figure.autofmt_xdate(rotation=45)
        #self.axes.axis("off")
        self.axes.set_title(self.tentukanJudul())
        
        self.canvas.draw()
        

    def buatPie(self):
        self.canvas.setVisible(True)
        self.toolbar.setVisible(True)
        self.tblCategory.setVisible(False)
        self.btSimpan.setVisible(False)
        
        #Select data if date 
        if self.boolChangedDateDate:
            self.selectDataBasedOnDate()
        #Fill in self.dataForGraph if it was emptied
        if not self.dataForGraph:
            self.selectDataBasedOnCategory()
        
        # Data to plot
        labels = []
        sizes = []
        
        for x, y in self.dataForGraph.items():
            labels.append(x)
            sizes.append(y)
        
        # Plot
        self.figure.clear()
        if self.globalDataForGraph:
            #print(self.globalDataForGraph)
            #Plotting globaldata
            glabels = []
            gsizes = []
            
            for x, y in self.globalDataForGraph.items():
                #glabels.append(x+'\n('+str(y)+')')
                glabels.append(x + ' (' + '{:.1%}'.format(y/len(self.df_ToDisplay)) + ')')
                
                #"{:.1%}".format(a_number)
                
                gsizes.append(y)
                #print(glabels)
                #print(gsizes)
            self.axes = self.figure.add_subplot(121)  
            #explode = (0.1, 0, 0)
            #self.axes.pie(gsizes, explode = explode, labels=glabels, autopct='%.1f%%', labeldistance=0.7)
            self.axes.pie(gsizes, labels=glabels, colors = ['lime','aquamarine', 'paleturquoise'],\
                          wedgeprops=dict(width=.6), textprops={'color': 'red'},\
                              labeldistance=0.5)
                
            self.axes.text(0., 0., 'Total\n' + str(len(self.df_ToDisplay)) + '\nTweets', horizontalalignment='center', verticalalignment='center')
            self.axes.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.

            
            #wedgeprops={'linewidth': 3.0, 'edgecolor': 'white'},
    
            #print(glabels)
            #print(gsizes)
            self.axes = self.figure.add_subplot(122)  
            self.axes.pie(sizes[:self.slJumlahKata.value()], labels=labels[:self.slJumlahKata.value()], wedgeprops=dict(width=.5), labeldistance=1)
            self.axes.text(0., 0., str(gsizes[-1]) + '\nTweets', horizontalalignment='center', verticalalignment='center')
            self.axes.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.

        else:
            self.axes = self.figure.add_subplot()  
            self.axes.pie(sizes[:self.slJumlahKata.value()], labels=labels[:self.slJumlahKata.value()])
        
        self.axes.set_title(self.tentukanJudul())
        self.canvas.draw()
        
        
    def buatTable(self):
        self.canvas.setVisible(False)
        self.toolbar.setVisible(False)
        self.tblCategory.setVisible(True)
        self.btSimpan.setVisible(True)

        #Select data if date 
        if self.boolChangedDateDate:
            self.selectDataBasedOnDate()
        #Fill in self.dataForGraph if it was emptied
        if not self.dataForGraph:
            self.selectDataBasedOnCategory()
        
        #Convert dictionary to dataframe
        
        
        
        if self.cbPilihKategori.currentText() == 'Tweet':
            model = pandasModel(self.df_tweet_RT)
            self.dfTableContent = self.df_tweet_RT
        else:
            df = pd.DataFrame(self.dataForGraph.items(), columns=[self.cbPilihKategori.currentText(), 'Frequency']).head(self.slJumlahKata.value())
            #print(df.head())
            
            if self.cbPilihKategori.currentText() == 'User':
                print(self.userCriteria)
                if self.userCriteria != 'Followers':
                    dict_followers = self.parent.parent.user_followers
                    df['Followers'] = df['User'].apply(lambda x: dict_followers[x] if x in dict_followers.keys() else -1)
                    
                    if self.userCriteria == 'Active':
                        df = df.rename(columns={'Frequency':'Number of Tweets'})
                    else:
                        df = df.rename(columns={'Frequency':'#' + self.userCriteria + 'ing Users'})
                    #print(df.head())
                    #print(self.userCriteria[:-2])
                else:
                    df = df.rename(columns={'Frequency':'Followers'})
            
            model = pandasModel(df)
            self.dfTableContent = df
            
        
        self.tblCategory.setModel(model)
        
       
        
    
    def nilaiJumlahKata(self,value):
        self.figure.clear()
        self.canvas.draw()
        self.dataForGraph = {}
        #self.lbJumlahKata.setText(str(value)+" top Tweets")
        self.lbJumlahKata.setText(str(value)+ " Top " + self.cbPilihKategori.currentText() + "s")
        
        
       
    def unggahStopWords(self):
        self.dataForGraph = {}
        filename = QFileDialog.getOpenFileName(self, 'Open File', os.getenv('HOME'))
        #if filename:
        if filename[0]:
            f = open(filename[0], 'r', encoding="utf-8")
            self.parent.parent.stopWords = f.read().split()
            #print('Stopwords tersimpan ......' + str(self.parent.parent.stopWords))
            
    def saveWordCloud(self):
        filename = QFileDialog.getSaveFileName(self, "Save Plot As", "plot.jpg", "*.jpg ;; *.png ;; *.pdf")
        savename = filename[0]
        if savename:
            if self.lbGraph.isVisible():
                self.result = self.lbGraph.grab()
                self.result.save(savename)
            
        
    def saveChart(self):
        filename = QFileDialog.getSaveFileName(self, "Save Plot As", "plot.jpg", "*.jpg ;; *.png ;; *.pdf")
        savename = filename[0]
        if savename:
            if self.cvCuitan.isVisible():
                self.result = self.cvCuitan.grab()
            else:
                self.result = self.cvPieTopN.grab()
            self.result.save(savename)

        
class tabData(QTabWidget):
    def __init__(self, parent): 
        #super(QWidget, self).__init__(parent) 
        super(QTabWidget, self).__init__(parent)
        self.parent = parent
        
        self.glayout = QGridLayout()
        
        self.btReadFile = QPushButton()
        self.btReadFile.setText('Upload File')
        self.btReadFile.clicked.connect(self.readFile)
        self.lbTanggal = QLabel()
        self.lbTanggal.setText('Date')
        self.rbDayFirst = QRadioButton("Day First")
        self.cbTanggal = QComboBox()
        self.lbID = QLabel()
        self.lbID.setText('ID')
        self.cbID = QComboBox()
        self.lbPengguna = QLabel()
        self.lbPengguna.setText('User')
        self.cbPengguna = QComboBox()
        self.lbCuitan = QLabel()
        self.lbCuitan.setText('Tweet')
        self.cbCuitan = QComboBox()
        
        self.lbRT = QLabel()
        self.lbRT.setText('Retweet')
        self.cbRT = QComboBox()
        
        self.lbYgDirespon = QLabel()
        self.lbYgDirespon.setText('Reply')
        self.cbYgDirespon = QComboBox()
        
        self.lbFollowers = QLabel()
        self.lbFollowers.setText('Followers')
        self.cbFollowers = QComboBox()
        
        self.btPilihKolom = QPushButton()
        self.btPilihKolom.setText('Select Columns')
        self.btPilihKolom.setDisabled(True)
        self.btPilihKolom.clicked.connect(self.selectColumns)
        
        self.tblData = QTableView()
  
        self.glayout.addWidget(self.btReadFile, 0, 0, 1, 2)
        self.glayout.addWidget(self.btPilihKolom, 0, 2, 1, 2)
        
        self.glayout.addWidget(self.lbTanggal,1, 1)
        self.glayout.addWidget(self.rbDayFirst, 2, 0)
        self.glayout.addWidget(self.cbTanggal,2, 1)
        
        
        self.glayout.addWidget(self.lbID, 1, 2)
        self.glayout.addWidget(self.cbID, 2, 2)
        
        self.glayout.addWidget(self.lbPengguna, 1, 3)
        self.glayout.addWidget(self.cbPengguna, 2, 3)
        
        self.glayout.addWidget(self.lbCuitan, 1, 4)
        self.glayout.addWidget(self.cbCuitan, 2, 4)
        
        self.glayout.addWidget(self.lbRT, 1, 5)
        self.glayout.addWidget(self.cbRT, 2, 5)
        
        self.glayout.addWidget(self.lbYgDirespon,1,6)
        self.glayout.addWidget(self.cbYgDirespon,2,6)
        
        self.glayout.addWidget(self.lbFollowers,1,7)
        self.glayout.addWidget(self.cbFollowers,2,7)
        
     
        self.glayout.addWidget(self.tblData,3,0,8,8)
        
         
        self.glayout.setRowStretch(3, 1) 
        
        self.setLayout(self.glayout) 
        

    def selectColumns(self):
        df = self.parent.parent.all_data
        
        df.drop_duplicates(subset = self.cbID.currentText(), keep = 'first', inplace=True)
        
        self.setEnabled(False)
        
        
        
        
        df = df.rename(columns={ self.cbTanggal.currentText(): 'Date', self.cbPengguna.currentText():'User',\
                                 self.cbCuitan.currentText(): 'Tweet', \
                                 self.cbYgDirespon.currentText(): 'Reply',\
                                 self.cbFollowers.currentText(): 'Followers'}  )
        
        
        df['User'] = df['User'].apply(lambda x: '@'+x)
        df['Tweet'] = df['Tweet'].str.replace('\n',' ')
        df['Followers'] = pd.to_numeric(df['Followers'])
        
        if self.cbRT.currentText() == 'Select':
            df['RT'] = df['Tweet'].str.findall(r'(?<=RT )@.*?(?=:)').apply(lambda x: ''.join(x))
        else:
            df = df.rename(columns={self.cbRT.currentText(): 'RT'}) 
            df['RT'] = df['RT'].apply(lambda x: '@'+x if x else '')
        
        df = df[['Date','User','Tweet', 'RT', 'Reply','Followers']]
        
        df['Hashtag'] = df['Tweet'].str.findall(r'#.+?(?=\W)')
        #df['Emoji'] = df['Tweet'].apply(lambda text: ' '.join([t for t in list(text) if t in emoji.UNICODE_EMOJI['en'].keys() and not t.isalpha()]))
        df['Mention']= df['Tweet'].str.findall(r'(?<!RT )@.*?(?=\s|$)')
        #df['Tautan'] = df['Tweet'].str.findall(r'http.*?(?=\s|$)')
        df['CuitBersih'] = df['Tweet'].apply(lambda x: ' '.join([a.lower() for a in x.split(' ') if not (a.startswith('RT') or a.startswith('@') or a.startswith('#')\
                                                  or a.startswith('http')) ]))\
            .apply(lambda x: re.sub(r'[^\w\s]', '', x))
        df['Reply'] = df['Reply'].apply(lambda x: '@'+str(x) if x != '' else '')
            
        self.parent.parent.all_data = df
        self.parent.parent.main_data = df
        
        if self.rbDayFirst.isChecked():
            dayfirst = True
        else:
            dayfirst = False
            
        df['Date'] = pd.to_datetime(df['Date'],dayfirst=dayfirst).dt.normalize()
        list_of_dates = list(df['Date'].unique())
        
        list_of_dates = sorted([ pd.to_datetime(d) for d in list_of_dates])
        
        #self.parent.parent.list_of_dates = list(set([d.strftime("%d/%m/%y") for d in list_of_dates]))
        #self.parent.parent.list_of_dates = [d.strftime("%d/%m/%y") for d in list_of_dates]
        
        self.parent.parent.list_of_dates = [d.strftime("%d/%m/%y") for d in list_of_dates]
        
        #self.parent.tabAwan.cbDariTanggal.addItems(['All']+self.parent.parent.list_of_dates)
        self.parent.tabFrequency.cbDariTanggal.addItems(self.parent.parent.list_of_dates)
        self.parent.tabFrequency.cbSampaiTanggal.addItems(self.parent.parent.list_of_dates)
        
        self.parent.parent.user_followers = df.groupby('User')['Followers'].max().to_frame().sort_values('Followers', ascending = False).to_dict()['Followers']
        
        
        
        model = pandasModel(df)
        self.tblData.setModel(model)
        
        self.parent.tabFrequency.setEnabled(True)
        
        self.parent.tabKata.setEnabled(True)
        
        #Write the name of the columns in a file in os.path.dirname()
        
        theLastColumns = [self.cbTanggal.currentText(), self.cbID.currentText(),\
                          self.cbPengguna.currentText(),\
                          self.cbCuitan.currentText(), self.cbRT.currentText(),\
                          self.cbYgDirespon.currentText(), self.cbFollowers.currentText()]
        textfile  = open(os.getcwd()+"/lastcols.txt", "w+")
        for element in theLastColumns:
            textfile.write(element + "\n")
        textfile.close()
        
        self.parent.tabs.setCurrentIndex(1)
        
        
        



    def readFile(self):
        #Reading data
        fnames = QFileDialog.getOpenFileNames(self, "Open Data File", "", "CSV data files (*.csv)")
        #print(fnames[0])
        if not fnames[0]:
            return
            
        #print(type(fnames))
        #print(fnames)
        list_of_files = []
        for fn in fnames[0]:
            list_of_files.append(pd.read_csv(open(fn, encoding = 'utf-8', errors = 'backslashreplace')))
            
        df = pd.concat(list_of_files, ignore_index=True)
        #df.drop_duplicates(keep=False,inplace=True)
        
        #Read lascols.txt to determine the default value of combobox, avoid rekeying
        theLastColumns = []
        
        #with open(os.getcwd()+"/lastcols.txt") as textfile:
        with open("lastcols.txt") as textfile:
            lines = textfile.readlines()
        textfile.close()
        for l in lines:
            theLastColumns.append(l.strip())
        
        daftar_kolom = ['Select'] + list(df.columns)
        
        self.parent.parent.all_data = df.replace(np.nan, '', regex=True)
        
        self.cbTanggal.addItems(daftar_kolom)
        self.cbID.addItems(daftar_kolom)
        self.cbPengguna.addItems(daftar_kolom)
        self.cbCuitan.addItems(daftar_kolom)
        self.cbRT.addItems(daftar_kolom)
        self.cbYgDirespon.addItems(daftar_kolom)
        self.cbFollowers.addItems(daftar_kolom)

        self.btPilihKolom.setEnabled(True)
        

        #print('Ini theLastColumns')
        #print(theLastColumns)
        
        if theLastColumns[0] in daftar_kolom:
            self.cbTanggal.setCurrentText(theLastColumns[0])
        if theLastColumns[1] in daftar_kolom:
            self.cbID.setCurrentText(theLastColumns[1])
        if theLastColumns[2] in daftar_kolom:
            self.cbPengguna.setCurrentText(theLastColumns[2])
        if theLastColumns[3] in daftar_kolom:
            self.cbCuitan.setCurrentText(theLastColumns[3])
        if theLastColumns[4] in daftar_kolom:
            self.cbRT.setCurrentText(theLastColumns[4])
        if theLastColumns[5] in daftar_kolom:
            self.cbYgDirespon.setCurrentText(theLastColumns[5])
        if theLastColumns[6] in daftar_kolom:
            self.cbFollowers.setCurrentText(theLastColumns[6])
        
        
        model = pandasModel(df)
        self.tblData.setModel(model)
        
            
class pandasModel(QAbstractTableModel):

    def __init__(self, data):
        QAbstractTableModel.__init__(self)
        self._data = data

    def rowCount(self, parent=None):
        return self._data.shape[0]

    def columnCount(self, parnet=None):
        return self._data.shape[1]

    def data(self, index, role=Qt.DisplayRole):
        if index.isValid():
            if role == Qt.DisplayRole:
                return str(self._data.iloc[index.row(), index.column()])
        return None
    

    def headerData(self, col, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self._data.columns[col]
        return None
    
class pandasModelKWIC(pandasModel):
    def data(self, index, role = Qt.DisplayRole):
        column = index.column()
        row = index.row()

        if role == Qt.DisplayRole:
            return str(self._data.iloc[index.row(), index.column()])
        elif role == Qt.BackgroundRole:
            if index.column() == 2:
                return QBrush(QColor(230,230,230))
                #return QBrush(Qt.green)
            elif index.row() % 2 == 0:
                return QBrush(QColor(240,240,240))
            else:
                return QBrush(Qt.white)
            
            
            #return QColor(Qt.white)
        elif role == Qt.TextAlignmentRole:
            if index.column() == 0:
                return Qt.AlignLeft
            if index.column() == 1:
                return Qt.AlignRight
            elif index.column() == 2:
                return Qt.AlignCenter
            if index.column() == 3:
                return Qt.AlignLeft
            else:
                return Qt.AlignLeft

        return None
    

    def headerData(self, col, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self._data.columns[col]
        elif role == Qt.BackgroundRole:
            return QBrush(Qt.green)
        return None
 
       
  
if __name__ == '__main__': 
    app = QApplication(sys.argv) 
    ex = App() 
    sys.exit(app.exec_()) 