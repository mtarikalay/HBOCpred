# Önceki revizyon notları

Bu dosya tarihsel R4 çalışma notlarını korur. Güncel durum için `SON_KONTROL_TR.md` ve `DEPOSITION_TR.md` esas alınmalıdır: 7 Eylül 2026 tarihinde katkı/finansman beyanları tamamlandı, beş kaynak düzeltildi ve canlı Shiny testi yazar tarafından teyit edildi.

# Reviewer 1, ikinci tur: tamamlanan iş ve gönderim öncesi kalanlar

Son yüklenen `ijms-4511203(7).docx` esas alındı. **35 kaynak, 26 Mendeley atıf alanı ve 1 bibliyografya alanı** var. Atıf alanı sayısı kaynak sayısı değildir: tek alan birden çok kaynağa atıf yapabilir. 35 kaynak paragrafı ve tüm alan talimatları korundu. Introduction'ın literatür paragrafları ile Discussion'ın kaynaklı ana karşılaştırma paragrafı değiştirilmedi. Amaç paragrafı, sonuçlara bağlı yorumlar ve yöntem/sınırlılık bölümleri düzeltildi. Word dosyaları mevcut IJMS şablonundan düzenlendi; ayrıca şablonda kalmış Molecules üstbilgisi IJMS olarak düzeltildi.

## Bilimsel olarak ne değişti?

Bu paket eski sayıların tekrar yazılması değildir. Ham kaynaklardan yeniden oluşturulan girdilerle 58 gerçek fit üretildi. Uygulama verisinden hesaplanan eksiklik filtresi kaldırıldı. Özellik seçimi, imputasyon ve ölçekleme iç eğitim foldlarının içinde de yeniden yapıldı. Reliability_index ana modelden çıkarıldı; katkısı ayrıca yeniden eğitimle incelendi. Gene göre 17 ayrı holdout, gen kimliğinin geri tahmini, gen prevalansı temel modeli, addAF/AlphaMissense çıkarma ve transkript-missense duyarlılık analizleri yapıldı.

Eksiklik kuralı değerlendirmede de uygulandığında 114 anchor çıktı alamıyor. Bu nedenle performans her tekrarda 2.046 değerlendirilebilir anchor üzerinde raporlandı; 2.160'ın tamamına veya VOUS kataloğuna genellenmedi. NR grubunun tamamı eksik olduğundan eski 22/23 iddiası kaldırıldı. İlk tekrarda 32 LP/P anchor V0 alıyor; bu risk metin ve Abstract'ta görünür. Aynı V0 / mixed / V4 yön tanımları hem anchor hem uygulamada kullanılıyor.

## gnomAD için araştırmanın sonucu

gnomAD'ı benign aday seçmek için kullanmak tek başına yanlış değil. Sık gözlenen varyantlar, uygun gen/hastalık kuralları ve BA1 istisnaları kontrol edilirse, benign yönde bir kontrol grubu oluşturabilir. Ancak AF ile seçilen örneklerde frekans bilgisini kullanan bir modelin iyi davranması, bağımsız klinik doğruluk kanıtı değildir. Hakemin asıl güçlü itirazı bu bağımlılık ve hedef popülasyona benzemeyen örnek seçimidir.

Benign ve patojenik örneklerin mutlaka aynı veri tabanından gelmesi gerekmez. Güvenilir etiketli tek sınıflı bir seri kendi sınıfındaki yakalama veya karşı-yön çıktı oranını gösterebilir; buna karşılık iki ayrı seçilmiş kaynağı birleştirmek genel doğruluk veya klinik prediktif değerleri geçerli kılmaz. Hastane listesinde bağımsız sınıflama kanıtları bulunmadığından yeni bir dış doğrulama sonucu yazılmadı. Tablo 5 artık 47 kapsam içi kaydın tamamından elde edilen 31 farklı missense varyantı içeriyor. Bunların 22’si anchor, sekizi uygulama kataloğu, biri anchor dışındaki kaynak arşiviyle örtüşüyor. Tamamı donmuş modelle skorlandı; anchor sonuçları eğitim içidir, dış doğrulama değildir. Tüm 122 satır ve 75 kapsam dışı kayıt denetimde korunuyor.

17 genin tamamındaki yeni gnomAD taramasında 50 gen düzeyinde missense aday bulundu. **47'si 7.137 satırlık eğitim arşivinde, bunların 45'i 2.160 anchor'da; bir başka aday VOUS arşivinde. Yalnız iki aday her iki arşiv dışında.** Bunlar CHEK2 ve PTEN'de alternatif transkriptlerde missense; MANE'de missense değiller. Bu iki varyantı “missense değil” diye silmedik, ancak tam transkript-uyumlu model girdisi olmadan skor üretmedik. BRCA1/BRCA2/PALB2 ağırlıklı 50 yeni ve bağımsız aday varmış gibi bir örneklem oluşturmadık; eşiği sayıyı doldurmak için değiştirmedik.

BA1 kaynağı: Ghosh ve ark., 2018, doi:10.1002/humu.23642; https://clinicalgenome.org/docs/updated-recommendation-for-the-benign-stand-alone-acmg-amp-criterion/. MANE kaynağı: https://www.ncbi.nlm.nih.gov/refseq/MANE/. Bu teknik kaynaklar makaledeki 35 Mendeley kaynağına otomatik eklenmedi.

## Gönderim öncesi gerçek açık işler

1. **Kalıcı depo ve DOI:** Paket hazırlanmış ve doğrulanmış durumda, fakat bir DOI alınmış değil; özel GitHub deposu `mtarikalay/HBOCpred` olarak belirlendi. Hakem özellikle bunu önkoşul yapıyor. Yükleme tamamlandıktan sonra gerçek DOI/erişim adresi Data/Code Availability ile yanıtın 8. maddesine işlenmeli ve hakem erişimi kontrol edilmeli. Makale ve yanıt bunu şu anda açıkça “pending” olarak belirtiyor.
2. **Shiny:** R4.4 arayüzünde başlık, filtreler, kartlar ve tablo görünümü yenilendi; dar ekran düzeni eklendi. R4 veri ve analiz sonuçları aynı. Sekiz R/Shiny çalışma kontrolü ve yerel dağıtım ön kontrolü geçti; tarayıcı kanıtı ayrı kaydedildi. Kayıtlı alaymd hesabı bulunmadığından canlı dağıtım yapılmadı. `shiny/deploy_hbocpred.R`, hesabın bağlı olduğu RStudio’da uygulamayı yükleyip kontrol ettikten sonra mevcut siteyi günceller.
3. **Yazar beyanları:** Finansman ve hasta/kamu katılımı beyanları, ayrıca varsa özgün ClinVar/dbNSFP/VEP sürüm-tarihleri kaynak materyalde yeterince kayıtlı değil. Bunlara ilişkin gerçek bilgileri yazar tamamlamalı; otomatik “yok” veya hayalî sürüm tarihi yazılmadı.
4. **Yeni patojenik dış seri:** İleride eklenecek satırlar için transkriptin sürümü, genomik kimlik/build, gerçek B/LB veya LP/P etiketi, etiketi destekleyen kanıt, sınıflama tarihi ve PP3/BP4 katkısı kaydedilmeli. 122 satırlık yüklenen liste `audit/hospital_source_curation.csv` içinde doldurulabilir biçimde hazır; boş etiketler LP/P kabul edilmedi. Bu yeni seri olmadan makale bağımsız klinik doğrulama iddiası taşımıyor.

Hakemin tüm bilimsel kaygılarının ortadan kalktığını veya kabulün garanti olduğunu söylemek doğru olmaz. Bu revizyon, düzeltilebilen yöntem ve raporlama sorunlarını gerçek analizlerle düzeltir; çözülemeyen bağımsız referans standardı, tarihsel transkript kaydı ve klinik genellenebilirlik sorunlarını iddianın sınırına dönüştürür. DOI adımı tamamlanmadan gönderime hazır denmemelidir.

## Claude değerlendirmesi sonrası son düzeltmeler

- Dokuz esas hakem yorumu artık birebir alıntı. Hakeme ait olmayan 10. madde kaldırıldı; ek kontroller ayrı yazar düzeltmeleri bölümünde. Mektubun üstündeki yazar notu silindi.
- gnomAD sonuç paragrafı kısaltıldı; ek materyaller ve atıfları birlikte korundu.
- Claude Tablo 8 doğrudan aktarılmadı: CHEK2 Ile200Thr / Ile157Thr aynı rs17879961 alelinin transkript karşılıkları. Yedi isim altı benzersiz genomik varyanta karşılık geliyor. Çıplak c.599T>C araması başka bir CHEK2 alelini seçiyordu. Bu altı örnek, son genişletmede 31 varyantlık tam Tablo 5’nin bir alt kümesidir. Gly210Arg/Gly167Arg da aynı CHEK2 aleline karşılık geldiğinden birleştirildi; Ile157Thr V0, S_MAC 0,0093.
- Teslim ZIP’i açıldı; 58 dolu model, 50 gnomAD kaydı doğrulandı. Modellerden tüm kayıtlı tahminler yeniden üretildi; en büyük fark 1,11×10⁻¹⁶.
- Ek materyaldeki BA1 yöntem kaynağının hatalı dergi/DOI bilgisi düzeltildi: Human Mutation 2018;39:1525–1530, 10.1002/humu.23642. Makalenin 35 Mendeley kaynağı değiştirilmedi.

Bugünkü gönderim için kalıcı depo/DOI, canlı Shiny yayımlaması ve eksik yazar beyanları hâlâ sizin hesap/gerçek bilgi girişinizi gerektiriyor. Hazır olmayan bir depo için yapılmış ifadesi eklenmedi.

Son belge ve kaynak kontrolü: `SON_KONTROL_TR.md`.
