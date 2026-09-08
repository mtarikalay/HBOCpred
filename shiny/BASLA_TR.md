# HBOCpred’i mevcut web adresinde güncelle

Bu paket R4.3 arayüzünü içerir: lacivert–turkuaz başlık, daha okunaklı özet kartları, sade filtreler ve telefon ekranına uyarlanan tablo düzeni. Bir varyant seçildiğinde dört modelin grafiği açılır. Katalog ve Model audit sekmeleri korunur. R4 analiz sonuçları ve 43.679 varyantın skorları aynıdır.

1. ZIP’i yeni bir klasöre çıkar ve içindeki **HBOCpred.Rproj** dosyasını RStudio ile aç.
2. Çalışan yerel uygulamayı **Stop** ile durdur.
3. Konsolda aşağıdaki komutları çalıştır:

```r
source("deploy_hbocpred.R")
deploy_hbocpred()
```

Betik önce uygulamayı yerel olarak yükler ve katalog bütünlüğünü kontrol eder; ardından mevcut **alaymd/hbocpred** uygulamasını gerçek uygulama ID’siyle günceller.

Eksik paket hatası alırsan R oturumunu yeniden başlat ve Windows’ta şunu çalıştır:

```r
install.packages(c("shiny", "DT", "jsonlite", "rsconnect"),
                 repos = "https://cloud.r-project.org", type = "binary")
```

Hesap kayıtlı değilse RStudio’da **Tools > Global Options > Publishing > Connect > ShinyApps.io** üzerinden mevcut **alaymd** hesabını bağla. Hesap bilgilerini yalnız kendi bilgisayarında kullan.

Yalnız yerel kontrol için `deploy_hbocpred(check_only = TRUE)`; önizleme için `source("run_local.R")` çalıştır.

Dağıtım başarıyla bitince https://alaymd.shinyapps.io/hbocpred/ adresini yenile. İki sekme görünmeli: **Variant catalogue** ve **Model audit**. Filtresiz sayımlar **43.679 / 33.414 / 4.491 / 5.774** olmalı.

Bu hazırlama ortamından canlı dağıtım yapılmadı; hesabın bağlı olduğu RStudio’daki dağıtım komutunun tamamlanması gerekir. R4.3 için sekiz R/Shiny çalışma kontrolü ve yerel dağıtım ön kontrolü geçti. Tarayıcı kontrolleri `tests/browser_verification.json`, önceki sürüm kayıtları `tests/history_R4_1/` ve `tests/history_R4_2/` içinde bulunur.
