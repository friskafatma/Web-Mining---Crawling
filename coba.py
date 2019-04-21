import requests
from bs4 import BeautifulSoup
import sqlite3
import csv
from Sastrawi.Stemmer.StemmerFactory import StemmerFactory
from Sastrawi.StopWordRemover.StopWordRemoverFactory import StopWordRemoverFactoryfrom math import log10
import numpy as np
from sklearn.metrics import silhouette_samples, silhouette_score
import skfuzzy as fuzz

conn = sqlite3.connect('articles.sqlite')
conn.execute('DROP TABLE if exists articles')
conn.execute('''CREATE TABLE ARTICLES
                (TITLE         TEXT     NOT NULL,
                 ISI         TEXT     NOT NULL);''')
conn.commit()
src = "https://thegorbalsla.com/category/pendidikan/"

n = 1
while n <= 15:
    print(n)
    page = requests.get(src)
    soup = BeautifulSoup(page.content, 'html.parser')
                
    linkhead = soup.findAll(class_='read-more')
    nextpage = soup.find(class_='next page-numbers')
      
    for links in linkhead:
        try :
            src = links['href']
            page = requests.get(src)
            soup = BeautifulSoup(page.content, 'html.parser')

            konten = soup.find('article')
            title = konten.find(class_='entry-title').getText()
            temp = konten.findAll('p')

            isi = []
            for j in range(len(temp)):
                isi += [temp[j].getText()]

            isif = ""
            for i in isi:
                isif += i
            conn.execute("INSERT INTO ARTICLES (TITLE, ISI) VALUES (?, ?)", (title, isif));

        except AttributeError:
            continue
    conn.commit()
    src = nextpage['href']
    n+=1
    
def write_csv(nama_file, isi, tipe='w'):
    'tipe=w; write; tipe=a; append;'
    with open(nama_file, mode=tipe) as tbl:
        tbl_writer = csv.writer(tbl, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        for row in isi:
            tbl_writer.writerow(row)
            
cursor = conn.execute("SELECT* from ARTICLES")
factory = StopWordRemoverFactory()
stopword = factory.create_stop_word_remover()
from Sastrawi.Stemmer.StemmerFactory import StemmerFactory
factory = StemmerFactory()
stemmer = factory.create_stemmer()
stop = stopword.remove(isif)
stem = stemmer.stem(stop)
katadasar = stem.split()

matrix=[]
for row in cursor:
    tampung = []
    for i in katadasar:
        tampung.append(row[1].lower().count(i))
    matrix.append(tampung)

write_csv("kata_before.csv", katadasar)

conn = sqlite3.connect('KBI.db')
cur_kbi = conn.execute("SELECT* from KATA")

def LinearSearch (kbi,kata):
    found=False
    posisi=0
    while posisi < len (kata) and not found :
        if kata[posisi]==kbi:
            found=True
        posisi=posisi+1
    return found

berhasil=[]
berhasil2=''
for kata in cur_kbi :
    ketemu=LinearSearch(kata[0],katadasar)
    if ketemu :
        kata = kata[0]
        berhasil.append(kata)
        berhasil2=berhasil2+' '+kata
print(berhasil)

conn = sqlite3.connect('articles.sqlite')
matrix2=[]
cursor = conn.execute("SELECT* from ARTICLES")
for row in cursor:
    tampung = []
    for i in berhasil:
        tampung.append(row[1].lower().count(i))
    matrix2.append(tampung)
print(matrix2)

write_csv("kata_after.csv", berhasil)


df = list()
for d in range (len(matrix2[0])):
    total = 0
    for i in range(len(matrix2)):
        if matrix2[i][d] !=0:
            total += 1
    df.append(total)

idf = list()
for i in df:
    tmp = 1 + log10(len(matrix2)/(1+i))
    idf.append(tmp)

tf = matrix2
tfidf = []
for baris in range(len(matrix2)):
    tampungBaris = []
    for kolom in range(len(matrix2[0])):
        tmp = tf[baris][kolom] * idf[kolom]
        tampungBaris.append(tmp)
    tfidf.append(tampungBaris)
print("satu")

write_csv("tfidf.csv", tfidf)


def pearsonCalculate(data, u,v):
    "i, j is an index"
    atas=0; bawah_kiri=0; bawah_kanan = 0
    for k in range(len(data)):
        atas += (data[k,u] - meanFitur[u]) * (data[k,v] - meanFitur[v])
        bawah_kiri += (data[k,u] - meanFitur[u])**2
        bawah_kanan += (data[k,v] - meanFitur[v])**2
    bawah_kiri = bawah_kiri ** 0.5
    bawah_kanan = bawah_kanan ** 0.5
    return atas/(bawah_kiri * bawah_kanan)
def meanF(data):
    meanFitur=[]
    for i in range(len(data[0])):
        meanFitur.append(sum(data[:,i])/len(data))
    return np.array(meanFitur)
def seleksiFiturPearson(data, threshold, berhasil):
    global meanFitur
    data = np.array(data)
    meanFitur = meanF(data)
    u=0
    while u < len(data[0]):
        dataBaru=data[:, :u+1]
        meanBaru=meanFitur[:u+1]
        seleksikata=berhasil[:u+1]
        v = u
        while v < len(data[0]):
            if u != v:
                value = pearsonCalculate(data, u,v)
                if value < threshold:
                    dataBaru = np.hstack((dataBaru, data[:, v].reshape(data.shape[0],1)))
                    meanBaru = np.hstack((meanBaru, meanFitur[v]))
                    seleksikata = np.hstack((seleksikata, berhasil[v]))
            v+=1
        data = dataBaru
        meanFitur=meanBaru
        berhasil=seleksikata
        if u%50 == 0 : print("proses : ", u, data.shape)
        u+=1
    return data, seleksikata

xBaru2,kataBaru = seleksiFiturPearson(tfidf, 0.9, berhasil)
xBaru1,kataBaru2 = seleksiFiturPearson(xBaru2, 0.8, berhasil)

write_csv("kata_baru.csv", kataBaru2)
print(xBaru2)

print("Cluster dgn Seleksi Fitur : 0.8")
cntr, u, u0, distant, fObj, iterasi, fpc =  fuzz.cmeans(xBaru1.T, 3, 2, 0.00001, 1000, seed=0)
membership = np.argmax(u, axis=0)

silhouette = silhouette_samples(xBaru1, membership)
s_avg = silhouette_score(xBaru1, membership, random_state=10)

for i in range(len(tfidf)):
    print("c "+str(membership[i]))
print(s_avg)

write_csv("ClusterFS8.csv", [["Cluster"]])
write_csv("ClusterFS8.csv", [membership],        "a")
write_csv("ClusterFS8.csv", [["silhouette"]],    "a")
write_csv("ClusterFS8.csv", [silhouette],        "a")
write_csv("ClusterFS8.csv", [["Keanggotaan"]],   "a")
write_csv("ClusterFS8.csv", u,                   "a")
write_csv("ClusterFS8.csv", [["pusat Cluster"]], "a")
write_csv("ClusterFS8.csv", cntr,                "a")

