# Phân tích 1 dạng thời khóa biểu của bản thân để lưu vào database
    - Tên hoạt động
    - ngày tháng
    - thứ trong tuần
    - thời gian bắt đầu
    - thời gian kết thúc
    - thời gian thực hiện
    - thời gian hoàn thành
    - kêt quả đạt được
    - Địa điểm
    - Loại hoạt động
    - Mô tả chi tiết
    - Màu sắc
    - phần thưởng

# Phần create
    - Tên hoạt động
    - ngày tháng
    - thứ trong tuần
    - thời gian bắt đầu
    - thời gian kết thúc
    - Địa điểm (optional)
    - Loại hoạt động (optional)
    - Mô tả chi tiết (optional)
    - Màu sắc (optional)
    
# SQL Tương ứng
    CREATE TABLE schedules (
        schedule_id INT PRIMARY KEY AUTO_INCREMENT,
        user_id INT NOT NULL,
        activity_name VARCHAR(100) NOT NULL,
        start_time DATETIME NOT NULL,
        end_time DATETIME NOT NULL,
        executime_time DATETIME,
        finished_time DATETIME,
        result varchar(1000),
        day_of_week ENUM('Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday') NOT NULL ,  -- "Monday", "Tuesday",...
        location VARCHAR(200),
        activity_type VARCHAR(50),
        description varchar(1000),
        color VARCHAR(10) DEFAULT '#3498db',
        FOREIGN KEY (user_id) REFERENCES users(id)
    );
