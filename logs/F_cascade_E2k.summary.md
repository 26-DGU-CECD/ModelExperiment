# F_cascade_E2k

gate=E2k_v2 (event score = 1 - p_bg, thr 0.2581 for val event recall >= 0.99), classifier=E0m_v2

- val: macro-F1 0.9264 emerg recall 0.9616922051965356 bg FA 0.1482213438735178 strict 0.006053268765133172 | gate pass 0.826 (events 0.9901036757775683, bg 0.3669301712779974) expected MACs 0.161G (-25.6% vs E0m_v2)
- test: macro-F1 0.9097 emerg recall 0.9583854818523154 bg FA 0.16099290780141845 strict 0.007894736842105263 | gate pass 0.823 (events 0.9798522498321021, bg 0.324822695035461) expected MACs 0.160G (-25.2% vs E0m_v2)
- noisy_snr20: macro-F1 0.8562 emerg recall 0.8282227784730913 bg FA 0.1773049645390071 strict None | gate pass 0.863 (events 0.9782852025968212, bg 0.49858156028368794) expected MACs 0.165G (-29.3% vs E0m_v2)
- noisy_snr15: macro-F1 0.8451 emerg recall 0.8235294117647058 bg FA 0.19432624113475178 strict None | gate pass 0.867 (events 0.9778374748153122, bg 0.5141843971631206) expected MACs 0.166G (-29.6% vs E0m_v2)
- noisy_snr10: macro-F1 0.8226 emerg recall 0.8132040050062578 bg FA 0.2148936170212766 strict None | gate pass 0.873 (events 0.9764942914707858, bg 0.5460992907801419) expected MACs 0.167G (-30.3% vs E0m_v2)

# F_cascade_E2k

gate=E2k_v2 (event score = 1 - p_bg, thr 0.2581 for val event recall >= 0.99), classifier=E0m_v2

- val: macro-F1 0.9264 emerg recall 0.9616922051965356 bg FA 0.1482213438735178 strict 0.006053268765133172 | gate pass 0.826 (events 0.9901036757775683, bg 0.3669301712779974) expected MACs 0.161G (-25.6% vs E0m_v2; pure-bg stream 0.102G +20.3%)
- test: macro-F1 0.9097 emerg recall 0.9583854818523154 bg FA 0.16099290780141845 strict 0.007894736842105263 | gate pass 0.823 (events 0.9798522498321021, bg 0.324822695035461) expected MACs 0.160G (-25.2% vs E0m_v2; pure-bg stream 0.097G +24.5%)
- noisy_snr20: macro-F1 0.8562 emerg recall 0.8282227784730913 bg FA 0.1773049645390071 strict None | gate pass 0.863 (events 0.9782852025968212, bg 0.49858156028368794) expected MACs 0.165G (-29.3% vs E0m_v2; pure-bg stream 0.119G +7.2%)
- noisy_snr15: macro-F1 0.8451 emerg recall 0.8235294117647058 bg FA 0.19432624113475178 strict None | gate pass 0.867 (events 0.9778374748153122, bg 0.5141843971631206) expected MACs 0.166G (-29.6% vs E0m_v2; pure-bg stream 0.121G +5.6%)
- noisy_snr10: macro-F1 0.8226 emerg recall 0.8132040050062578 bg FA 0.2148936170212766 strict None | gate pass 0.873 (events 0.9764942914707858, bg 0.5460992907801419) expected MACs 0.167G (-30.3% vs E0m_v2; pure-bg stream 0.125G +2.4%)

# F_cascade_E2k

gate=E2k_v2 (event score = 1 - p_bg, thr 0.2581 for val event recall >= 0.99), classifier=E0m_v2

- val: macro-F1 0.9264 emerg recall 0.9616922051965356 bg FA 0.1482213438735178 strict 0.006053268765133172 | gate pass 0.826 (events 0.9901036757775683, bg 0.3669301712779974) expected MACs 0.161G (-25.6% vs E0m_v2; pure-bg stream 0.102G +20.3%)
- test: macro-F1 0.9097 emerg recall 0.9583854818523154 bg FA 0.16099290780141845 strict 0.007894736842105263 | gate pass 0.823 (events 0.9798522498321021, bg 0.324822695035461) expected MACs 0.160G (-25.2% vs E0m_v2; pure-bg stream 0.097G +24.5%)
- noisy_snr20: macro-F1 0.8562 emerg recall 0.8282227784730913 bg FA 0.1773049645390071 strict None | gate pass 0.863 (events 0.9782852025968212, bg 0.49858156028368794) expected MACs 0.165G (-29.3% vs E0m_v2; pure-bg stream 0.119G +7.2%)
- noisy_snr15: macro-F1 0.8451 emerg recall 0.8235294117647058 bg FA 0.19432624113475178 strict None | gate pass 0.867 (events 0.9778374748153122, bg 0.5141843971631206) expected MACs 0.166G (-29.6% vs E0m_v2; pure-bg stream 0.121G +5.6%)
- noisy_snr10: macro-F1 0.8226 emerg recall 0.8132040050062578 bg FA 0.2148936170212766 strict None | gate pass 0.873 (events 0.9764942914707858, bg 0.5460992907801419) expected MACs 0.167G (-30.3% vs E0m_v2; pure-bg stream 0.125G +2.4%)

