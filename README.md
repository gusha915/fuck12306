fuck 12306
目前只支持刷票，改签没有测试。

## 运行

1 编辑 hcclient.py 填写账号信息和车次信息

```
python hcclient.py
```

2 请输入验证码图片序号，以空格或逗号分割:3 6
（3 6）表示第三张图片和第6张图片


成功的话就会显示

```
正在购买[ 2018-01-18 ]，车次 C6802 [ IOQ - KNQ ][06:35-07:02]
获取token成功 ....
获取train_no成功 .....
获取leftticketstr成功 ....
获取purpose_codes成功 ...
获取train_location成功 ....
获取key_check_isChange成功 .....
checkorderinfo .....
waitCount 0
貌似购买成功了？
over...
```