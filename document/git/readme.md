### Kết nối server git
    - echo "# course" >> README.md
    - git init
    - git add README.md
    - git add -A
    - git commit -m "first commit"
    - git branch -M main
    - git remote add origin https://github.com/vutuankhac/course.git
    - git push -u origin main
    
### Thực hiện sửa đổi file và commit lên github
    - sửa file
    - git status
    - git add <tên file>
    - git commit -m"<message>" 
    - git push
   - neu duoc yeu cau nhap username + email thi su dung
    - git config --local user.email "<email của bạn>"
    - git config --local user.name "<tên của bạn>"
    
### Trường hợp ai đó đã đẩy code lên git trước bạn
    - git pull
    