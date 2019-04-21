### PENAMBANGAN DAN PENCARIAN WEB

Friska Fatmawatiningrum (160411100084)



Target website : https://thegorbalsla.com/category/pendidikan/

Program yang dibutuhkan : Python 3.6 (dengan library requests, beautifulsoup4, sqlite3, csv, numpy, scikit-learn, sastrawi, scikit-fuzzy)



**Step :**

1. **Crawling Web** dIgunakan untuk mengambil data dari sebuah website, baik berupa text, citra, audio, video, dll. Dan kali ini akan mengambil data berupa text saja. Dengan meng-import library BeautifulSoup4 terlebih dahulu 

   ```
   from bs4 import BeautifulSoup
   ```



   Code program :

   ```
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
   ```

   Terlebih dahulu dibuat database nya dengan sqlite3  dan diconnect kan dengan sqlite, database bernama articles, dengan tabel articles yang mempunyai atribut title dan isi.

   ```
   conn = sqlite3.connect('articles.sqlite')
   conn.execute('DROP TABLE if exists articles')
   conn.execute('''CREATE TABLE ARTICLES
                   (TITLE         TEXT     NOT NULL,
                    ISI         TEXT     NOT NULL);''')
   conn.commit()
   ```

   kemudian link website yang di crawl disimpan di variable src 

   ```
   src = "https://thegorbalsla.com/category/pendidikan/"
   ```

   perulangan dengan kondisi while dilakukan sebanyak 15 kali, karena saya melakukan crawling next page sebanyak 15 halaman dengan masing masing halaman berisi 3 artikel.

   ```
   linkhead = soup.findAll(class_='read-more')
   nextpage = soup.find(class_='next page-numbers')
   ```

   Menggunakan fungsi soup.find dan soup.findAll yang ada pada BeautifulSoup4 untuk mengambil data dari class yang diketahui saat inspect elemen html. variabel linkhead untuk masuk ke isi artikel dan variabel nextpage untuk masuk ke link page selanjutnya.

   ```
   konten = soup.find('article')
   title = konten.find(class_='entry-title').getText()
   temp = konten.findAll('p')
   ```

   Code diatas digunakan untuk mengcrawling isi dari artikel tersebut yang berada pada satu class bernama article, dan judul dimuat pada class yang ada di variabel title kemudian diambil textnya dengan getText(), sedangkan untuk setial kalimat isinya di muat dalam tag html <p> yang ada pada variable temp.

   kemudian terdapat perulangan untuk mengambil semua paragraf pada isi artikel setelah itu di insert kan ke dalam database yang sudah dibuat.



2. **Pre-processing** tahap ini dilakukan dengan beberapa tahapan :

   1. Stopword Removal, untuk menghilangkan kata yang tidak penting.

   2. Stemming, untuk mengubah suata kata yang berimbuhan menjadi kata dasar.

   3. Tokenisasi (n-gram), untuk memecah kalimat menjadi per-kata.


   Berikut Code programnya dengan menggunakan library Sastrawi :

   ```
   cursor = conn.execute("SELECT* from ARTICLES")
   factory = StopWordRemoverFactory()
   stopword = factory.create_stop_word_remover()
   from Sastrawi.Stemmer.StemmerFactory import StemmerFactory
   factory = StemmerFactory()
   stemmer = factory.create_stemmer()
   stop = stopword.remove(isif)
   stem = stemmer.stem(stop)
   katadasar = stem.split()
   ```

   Mengambil dari tabel articles di database kemudian dilakukan stopword, lalu stemming dan tokenisasi dengan fungsi split.

   ```
   matrix=[]
   for row in cursor:
       tampung = []
       for i in katadasar:
           tampung.append(row[1].lower().count(i))
       matrix.append(tampung)
   ```

   Kode diatas digunakan untuk memasukkan hasil preprocessing dalam matrix

   ```
   def write_csv(nama_file, isi, tipe='w'):
       'tipe=w; write; tipe=a; append;'
       with open(nama_file, mode=tipe) as tbl:
           tbl_writer = csv.writer(tbl, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
           for row in isi:
               tbl_writer.writerow(row)
   
   write_csv("kata_before.csv", katadasar)
   ```

   Function diatas digunakan untuk otomatis membuat dan membaca data csv dengan parameter nama_file, isi, dan tipe='w'. Kemudian disimpan di file csv kata_before.

   Agar kata dasar yang diambil beraturan maka kita deteksi yang sesuai dengan KBBI dan untuk itu kita membutuhkan database kata dari KBBI yang tersimpan di file database KBI.db.

   ```
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
   ```

   code diatas digunakan untuk mendeteksi katadasar yang sudah ditemukan pada proses preprocessing dicek kata dasarnya bersarkan KBBI dengan melihat di tabal KATA pada KBI.db.

3.  **Matrix VSM**, merupakan proses perhitungan kemunculan semua kata yang terdapat pada setiap dokumen.

   ```
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
   ```

   code diatas digunakan untuk menghitung banyaknya kemunculan seluruh kata yang ada pada setiap dokumen yang di crawling untuk proses deteksi ini membutuhkan waktu yang lama karena jumlahbkata yang banyak. Setelah itu prosesnya disimpan ke dalam file kata_after.csv yang telah mengalami pengecekan kata dasar sesuai KBBI.

4. **TF-IDF**, kependekan dari Term Frequence (Frekuensi kata) dan Invers Document Frequence (invers frekuensi dokumen) tahap ini menggunakan rumus yaitu TF X IDF. Seperti pada proses ketiga yaitu VSM sama-sama mencari frekuenci kata yang muncul maka untuk proses ini tinggal mencari IDF nya kemudian di gunakan rumus TF-IDF nya.

   Jika TF digunakan untuk mencari banyak kata yang muncul pada satu dokumen maka IDF digunakan untuk mengetahui dokumen yang mana saja yang memiliki kata kata yang sama.

   Berikut codenya :

   ```
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
   ```

   Hasil TF-IDF disimpan dalam file csv tfidf.csv

5. **Seleksi Fitur**, untuk mengurangi fitur / kata yang sangat banyak karena tidak semua kata sangat dibutuhkan oleh karena itu perlu dilakukan pengurangan fitur tanpa mengurangi kualitas hasil akhirnya yaitu dengan seleksi fitur. Dan pada tahap seleksi fitur ini metode yang digunakan dengan Pearson Correlation yaitu, setiap fitur akan dihitung korelasinya kemudian jika terdapat fitur yang nilainya hampir sama tingginya maka akan dibuang salah satunya.



   Berikut code programnya :

   ```
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
   ```

   ```
   write_csv("kata_baru.csv", kataBaru2)
   ```

   Kemudian hasil seleksi fitur disimpan kedalam file csv kata_baru.csv

6. **Clustering**, mengelompokkan kata berdasarkan ciri yang mirip dan pada program ini dapat dilihat dari ciri kata yang digunakan pada suatu dokumen atau artikel. Untuk clustering kali ini digunakan metode C-Means Fuzzy.



   ```
   cntr, u, u0, distant, fObj, iterasi, fpc =  fuzz.cmeans(xBaru1.T, 3, 2, 0.00001, 1000, seed=0)
   membership = np.argmax(u, axis=0)
   ```

   code diatas adalah untuk clustering dengan C-Means Fuzzy dengan menggunakan  data, jumlah cluster, bobot(pangkat m), batas error max, dan max iterasi.



   Setelah dilakukan clustering maka harus dicari nilai koefisien silhouette nya untuk melihat apakah hasilnya sudah bagus atau tidak. Nilai silhouette terletak antara -1 sampai 1 , hasil yang bagus adalah mendekati 1.

   ```
   silhouette = silhouette_samples(xBaru1, membership)
   s_avg = silhouette_score(xBaru1, membership, random_state=10)
   ```





**Note : website yang sudah saya crawling datanya telah mengalami perubahan pada tampilan websitenya yaitu html dan css nya ketika saya menuliskan tutorial ini tepatnya tgl 20 April 2019, data yang saya tutorialkan adalah data yang lama karena lebih banyak artikel yang diunggah**