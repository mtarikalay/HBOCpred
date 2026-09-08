# Son belge kontrolü — 7 Eylül 2026

Clean ve sarı vurgulu makale, Reviewer 1 ikinci tur yanıtı ve Ek Materyaller güncellendi. MDPI/IJMS şablonu, Mendeley alan yapısı ve 35 kaynak korunur. Ana metinde 8 şekil ve 7 tablo vardır. Şekil 7 R4.4 Shiny uygulamasının gerçek tarayıcı görüntüsüdür. Gen/dağılım kayması Şekil 6, iş akışı Şekil 8 olarak yer alır. Tam hastane tablosu, 47 kaynak satırından elde edilen 31 benzersiz missense varyantın tamamını içeren Tablo 5'tir.

## Bu turda tamamlananlar

- **Yazar katkıları:** Supervision ve writing—review/editing M.T.A. ve H.B.E.; diğer 11 listelenen rol yalnızca M.T.A. Kullanıcının 7 Eylül talebi esas alındı.
- **Finansman:** Önceki yazar beyanından “This research received no external funding.” geri eklendi.
- **Yapay zekâ:** İngilizce düzeltmeleri ve makale revizyonu, kod geliştirme/hata düzeltme ve figür/arayüz düzenlemesindeki gerçek kullanım Methods 4.10'da belirtildi; Acknowledgments kısa bir yönlendirme ve yazar sorumluluğu beyanı içerir. Kullanılmamış veya doğrulanmamış kesin model sürümleri uydurulmadı.
- **Kaynaklar:** 6'nın grup yazarı eklendi; 16 medRxiv ön baskısı ve DOI'siyle tamamlandı; 17 genel ACMG/AMP kılavuzu Richards ve ark. (2015) ile değiştirildi; 23 kitap bölümü olarak düzeltildi; 33'te başlık kalıntısı temizlendi. Görünen liste ve beş gömülü CSL kaydı eşleştirildi. Diğer kaynak metinleri korunur. Kaynakların sayfa sonunda bölünmesini önlemek için paragraf ayarı uygulandı.
- **Discussion:** Yazarın işaretlediği yedi paragraf 733 kelimeden 396 kelimeye, beş paragrafa indirildi. Tekrarlanan feragatler çıkarıldı; circularity, dağılım kayması, gen farklılıkları, hata asimetrisi, eksiklik ve transkript sınırları korundu. 114 incomplete anchor'ın 101'inin NR olduğu açıkça yazıldı. Çok değerli alanların sayısal ayrıştırma ayrıntısı Methods 4.3'te korunur. Introduction ve ana literatür karşılaştırması paragrafı değiştirilmedi.
- **Shiny:** Canlı testin tamamlandığı yazar tarafından 7 Eylül'de teyit edildi. Makale bunu yazar teyidi olarak aktarır; bu belge turunda canlı siteye yeni bir dağıtım veya bağımsız uzak tarayıcı testi yapıldığı iddia edilmez.

26 atıf alanı birden çok kaynağı kapsayabilir; 26 sayısı kaynak sayısı değildir. Toplam 35 kaynak, 26 atıf alanı ve bir bibliyografya alanı vardır. Hakemin dokuz esas yorumu birebir korunmuştur. Clean ve highlighted belgelerin görünen metinleri aynıdır; fark revizyon vurgusudur.

## Gönderim için açık kalanlar

1. **Kalıcı depo DOI'si ve hakem erişimi:** GitHub hedefi artık `mtarikalay/HBOCpred`; Private görünürlüğü ve yazma erişimi doğrulandı. Özel depo hakeme otomatik erişim sağlamaz. Bu ortamda Zenodo hesabına yazma bağlantısı yoktur; DOI ve hakem erişim testi hâlâ tamamlanmalıdır. Ayrıntı: `DEPOSITION_TR.md`.
2. **Mendeley Desktop metadata:** Son yüklemede Richards'ın gerçek Desktop kimliği bulundu ve korundu. Yeniden bağlama gerekmiyor; fakat 6, 16, 23 ve 33'te eski metadata geri gelmişti. Gömülü kayıtlar yeniden düzeltildi. Yeni bir Refresh öncesinde Desktop kayıtları da eşleştirilmeli; son toplam 35 olmalı. Açıklama: `reference_corrections/MENDELEY_DESKTOP_TR.md`.
3. **Hasta/kamu katılımı:** Katılım durumuna ilişkin yazar beyanı verilmedi. Ek Tablo S4 bunu açık tutar. Genel TRIPOD+AI tam uyum iddiası eklenmedi.

DOI ve hakem bağlantısı oluşunca makalenin Data/Code Availability paragrafları, yanıtın 8. maddesi, Ek Tablo S4, README ve CITATION.cff birlikte tamamlanmalıdır. Henüz bu dosyalar DOI koşulu tamamlanmış bir gönderim paketi değildir.

## Kontrol dayanakları

`audit/final_document_integrity.json` ve `audit/final_document_visual_QA.json` güncel belge denetimlerini içerir. İçeriği değişen sayfalar görsel olarak incelendi; diğer sayfaların gövdeleri önceki tüm-sayfa görsel denetimiyle piksel düzeyinde eşleştirildi. Güncellenen sayfa numaraları ayrıca kontrol edildi. `audit/author_reference_updates_*.json` kaynak değişikliklerini; `audit/discussion_concision_20260907.json` kısaltılan paragrafların önceki/sonraki metnini saklar. Bu turdaki kısaltma, yazarın sonraki talebidir; önceki kaynak düzeltme denetimlerindeki “metin değişmedi” ifadesi o aşamaya aittir.

213 veri, model ve tahmin dosyası önceki doğrulanmış paketle bayt düzeyinde aynıdır. Bu belge turunda model eğitimi veya tüm-model replay yeniden yapılmadı; `audit/model_verification.json` önceki tam replay kontrolünü saklar. Şekil/tabloların sayısal sonuçları değişmedi. Bağımsız klinik doğrulama ve tarihsel anotasyon sürümlerindeki boşluklar bilimsel sınırlılık olarak korunmaktadır.

## Son yükleme üzerine yapılan ek düzeltmeler

- Son yüklemedeki 37 kaynak 35'e geri getirildi; yeniden giren Alport/kardiyomiyopati atıfları çıkarıldı. Richards Desktop kimliği ve yazarın eklediği [22,33] korundu.
- Tablo 5'in 31 varyantı korundu. 22 anchor satırının tam kaynak muhasebesi amacıyla bulunduğu, dokuz anchor-dışı varyantın örnek çıktılar sunduğu açıklandı; bağımsız doğrulama iddiası eklenmedi.
- Yanıt mektubunda Shiny test ayrıntısı kısaltıldı, sayısal replay farkı audit dosyasında bırakıldı, “R4” yerine “current release” yazıldı. Dokuz hakem yorumu aynen korundu.
- AI açıklaması Methods içinde 4.10 başlığına alındı; Acknowledgments yönlendirmesi güncellendi. MDPI'nin resmî açıklaması Methods ve Acknowledgments yerleşimini destekler; ayrı başlığın zorunlu olduğu iddia edilmez.
- Clean ve highlighted ana belgeler 25, yanıt mektubu 7 sayfadır. Sayısal analizler ve model dosyaları yeniden üretilmedi.
- Depo adı ve erişimi sonradan güncellendi: `mtarikalay/HBOCpred` Private ve erişilebilir. Önceki 404 kayıtları tarihsel denetim kanıtıdır.
