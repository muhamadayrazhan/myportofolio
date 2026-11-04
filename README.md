Name : Muhamad Ayrazhan

NPM : 2506586236

Class : PBP E

### Tugas 1

1. Saya menggunakan elemen semantik HTML5 yaitu "section" dalam mebuat section experience untuk membantu saya memperjelas bahwa yang ada di dalam "section" itu adalah konten yang berdiri sendiri yaitu section "experience".

2. Tantangan yang saya temukan adalah terlalu banyak perangkat yang ukuran layarnya sangat beragam. Untuk menyelesaikan masalah ini, saya coba buka DevTools saat saya runservernya di lokal, lalu perhatikan dimensinya, tarik dari ukuran yang paling kecil ke besar pelan-pelan. Dari hasil pengamatan tersebut kita bisa lihat di titik apa design kita mulai berantakan dan barulah kita perbaiki design yang rusak.

3. Staticweb ini terbatas, kalau saya ingin mengubah isinya, saya harus build ulang kodenya dan deploy lagi dari awal dan ini mungkin akan sangat merepotkan kedepannya. Untuk proyek selanjutnya mungkin akan menambahkan fitur create, read, update, dan delete agar memudahkan saya untuk melakukan update informasi yang ada, seperti experience saya yang mungkin akan bertambah kedepannya.

### Tugas 2

1. Alur yang terjadi adalah saat kita mengetik di browser lalu membuka .../education/ misalnya, browser mengirim request lalu urls.py proyek meneruskan request ke urls.py aplikasi lalu urls.py aplikasi mencari request tersebut (dalam hal ini adalah education/) dan saat ketemu barulah views.py bekerja. views.py disini mengambil data dari tempatnya dan disinilah peran models.py yang mengatur bahwa data education itu harus memiliki nama institusi, jenjang, dan lainnya. Setelah itu, views.py mengirimkan data tadi ke template (dalam hal ini adalah education.html) untuk menampilkan data tersebut di browser pengguna.

2. Data ini lebih baik disimpan dalam model karena kalau aku mendapatkan pengalaman baru nantinya aku bisa masukkan datanya dengan mudah tanpa harus mengubah htmlnya karena jika tidak menggunakan model aku harus mengubah codenya dan itu sangat memakan waktu jika ditulis langsung di template. Hal ini juga sangat berguna untuk pemeliharaan dan pengembangan aplikasi karena model membuat kita bisa menggunakan tests untuk menguji apakah hal yang kita buat berfungsi, seperti memastikan objek benar benar muncul di halaman, dan lainnya.

3. Bedanya adalah, makemigrations adalah perintah untuk membuat file migrasi baru berdasarkan perubahan yang telah dibuat di dalam model. Lalu migrate adalah perintah yang digunakan agar file migrasi yang kita buat tersebut dapat diaplikasikan dan memastikan databasenya selalu sesuai dengan model yang sudah dibuat. Contoh perubahan yang mengharuskan keduanya adalah jika aku menambahkan field baru di model Education, contohnya aku tambahkan field IPK, maka aku harus menjalankan keduanya karena aku merubah model dan model tersebut harus diaplikasikan ke dalam database yang ada.