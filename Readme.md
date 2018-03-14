北京化工大学研究生教务管理系统选课脚本
===========
![py35][py35]

## 用法：

需要用到的第三方库：BeautifulSoup

首先修改lessonList.txt中的内容：

1. 第一行留空（因为在Win上使用notepad编辑会莫名奇妙多出几个字符，又不想把它去掉）
2. 第二行为用户名（学号）
3. 第三行为密码
4. 之后的每一行一门课的名称，注意：**不要带上班级**

```
python predator.py
```

若电脑上无python开发环境，点击[latest release]下载独立运行程序

---

## 缺陷

没花多少时间写的小脚本，各位大佬不喜勿喷

- 登陆时偷懒直接以服务器响应码作为是否成功登陆的判定条件，所以请保证用户名和密码正确
- 没办法选班级

[py35]: https://img.shields.io/badge/python-3.5-red.svg
[latest release]: https://github.com/ycZhou/Predator/releases