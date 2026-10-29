# F_cascade_E0m

gate=E0m_v2 (event score = 1 - p_bg, thr 0.5647 for val event recall >= 0.99), classifier=E0m_v2

- val: macro-F1 0.9187 emerg recall 0.9630246502331778 bg FA 0.1600790513833992 strict 0.007263922518159807 | gate pass 0.775 (events 0.9901036757775683, bg 0.1725955204216074) expected MACs 0.227G (-77.5% vs E0m_v2)
- test: macro-F1 0.9181 emerg recall 0.9699624530663329 bg FA 0.16666666666666666 strict 0.011842105263157895 | gate pass 0.796 (events 0.9932840832773674, bg 0.17304964539007092) expected MACs 0.230G (-79.6% vs E0m_v2)
- noisy_snr20: macro-F1 0.8638 emerg recall 0.8394868585732165 bg FA 0.17872340425531916 strict None | gate pass 0.801 (events 0.9928363554958585, bg 0.1950354609929078) expected MACs 0.231G (-80.1% vs E0m_v2)
- noisy_snr15: macro-F1 0.8470 emerg recall 0.8332290362953693 bg FA 0.20851063829787234 strict None | gate pass 0.810 (events 0.9932840832773674, bg 0.23049645390070922) expected MACs 0.232G (-81.0% vs E0m_v2)
- noisy_snr10: macro-F1 0.8256 emerg recall 0.8241551939924906 bg FA 0.23687943262411348 strict None | gate pass 0.824 (events 0.9939556749496307, bg 0.28581560283687946) expected MACs 0.233G (-82.4% vs E0m_v2)

# F_cascade_E0m

gate=E0m_v2 (event score = 1 - p_bg, thr 0.5647 for val event recall >= 0.99), classifier=E0m_v2

- val: macro-F1 0.9187 emerg recall 0.9630246502331778 bg FA 0.1600790513833992 strict 0.007263922518159807 | gate pass 0.775 (events 0.9901036757775683, bg 0.1725955204216074) expected MACs 0.227G (-77.5% vs E0m_v2; pure-bg stream 0.150G -17.3%)
- test: macro-F1 0.9181 emerg recall 0.9699624530663329 bg FA 0.16666666666666666 strict 0.011842105263157895 | gate pass 0.796 (events 0.9932840832773674, bg 0.17304964539007092) expected MACs 0.230G (-79.6% vs E0m_v2; pure-bg stream 0.150G -17.3%)
- noisy_snr20: macro-F1 0.8638 emerg recall 0.8394868585732165 bg FA 0.17872340425531916 strict None | gate pass 0.801 (events 0.9928363554958585, bg 0.1950354609929078) expected MACs 0.231G (-80.1% vs E0m_v2; pure-bg stream 0.153G -19.5%)
- noisy_snr15: macro-F1 0.8470 emerg recall 0.8332290362953693 bg FA 0.20851063829787234 strict None | gate pass 0.810 (events 0.9932840832773674, bg 0.23049645390070922) expected MACs 0.232G (-81.0% vs E0m_v2; pure-bg stream 0.158G -23.0%)
- noisy_snr10: macro-F1 0.8256 emerg recall 0.8241551939924906 bg FA 0.23687943262411348 strict None | gate pass 0.824 (events 0.9939556749496307, bg 0.28581560283687946) expected MACs 0.233G (-82.4% vs E0m_v2; pure-bg stream 0.165G -28.6%)

