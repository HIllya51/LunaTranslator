# Textractor

![How it looks](screenshot.png)

[English](README.md) ● [Español](README_ES.md) ● [简体中文](README_SC.md) ● [Русский](README_RU.md) ● [한국어](README_KR.md) ● [ภาษาไทย](README_TH.md) ● [Français](README_FR.md) ● [Italiano](README_IT.md) ● [日本語](README_JP.md) ● [Bahasa Indonesia](README_ID.md) ● [Português](README_PT.md)

**Textractor** (a.k.a NextHooker) adalah teks hooker video game untuk Windows/Wine x86/x64 berbasis open-source yang didasari oleh [ITHVNR](https://web.archive.org/web/20160202084144/http://www.hongfire.com/forum/showthread.php/438331-ITHVNR-ITH-with-the-VNR-engine).<br>
Lihat [video tutorial](docs/TUTORIAL.md) untuk mengetahui bagaimana cara menggunakannya.

## Pengunduhan

Rilisan Textractor dapat diunduh [disini](https://github.com/Artikash/Textractor/releases).<br>
Rilisan Terakhir ITHVNR dapat diunduh [disini](https://drive.google.com/open?id=13aHF4uIXWn-3YML_k2YCDWhtGgn5-tnO).

## Fitur

- Sangat Ekstensibel
- Tempel otomatis banyak engine game (termasuk beberapa yang tidak didukung oleh VNR)
- Hook teks menggunakan "hook" /H (mendukung semua kode AGTH)
- Mengutip teks secara langsung menggunakan kode /R "read"

## Dukungan

Tolong beritahu saya jika kamu menemukan kutu, game yang tidak dapat di tempel oleh Textractor, permintaan fitur, atau usulan lain.<br>
Jika kamu memiliki masalah dalam menempelkan kedalam game tolong email saya link agar saya dapat mengunduh game tersebut, atau hadiahkan game tersebut di [Steam](https://steamcommunity.com/profiles/76561198097566313/).

## Ekstensi

Lihat [project sampel ekstensi saya](https://github.com/Artikash/ExampleExtension) untuk melihat bagaimana cara membuat ekstensi.<br>
Lihat ekstensi folder untuk melihat sampel ekstensi.

## Kontribusi

Seluruh kontribusi diapresiasi! Tolong email saya di akashmozumdar@gmail.com jika kamu memiliki pertanyaan mengenai kode dasar nya.<br>
Kamu harus menggunakan proses standar dalam membuat permintaan pull(fork, cabang, perubahan commit, membuat PR dari cabang kamu ke master saya).<br>
Berkontribusi dalam penerjemahan dapat dilakukan dengan mudah : cukup terjemahkan string dari text.cpp lalu terjemahkan README ini.

## Mengcompile

Sebelum melakukan proses compile *Textractor*, kamu harus memiliki Visual Studio dengan dukungan Cmake, juga dengan Qt version 5.13<br>
Lalu kamu dapat membuka folder di Visual Studio, dan build. Jalankan Textractor.exe.


## Arsitektur Project

Host (lihat folder host) menyuntikan texthook.dll (dibuat dari folder texthook) kedalam target proses dan disambungkan lewat 2 file pipe.<br>
Host menulis ke hostPipe, texthook menulis ke hookPipe.<br>
texthook menunggu pipe tersambung, lalu menyuntikan beberapa instruksi ke teks yang menghasilkan fungsi (contoh: TextOut, GetGlyphOutline) yang membuat input dikirim melewati pipa.<br>
Informasi tambahan tentang hook dipindahkan melewati shared memory.<br>
Teks yang diterima host melewati pipe lalu diproses lagi sebelum dikembalikan ke GUI.<br>
Dan pada akhirnya, GUI melepas teks ke ekstensi sebelum menampilkan teks.

## [Pengembang](docs/CREDITS.md)
