class BalloonGame {
    constructor() {
        this.canvas = document.getElementById('gameCanvas');
        this.ctx = this.canvas.getContext('2d');
        this.canvas.width = 800;
        this.canvas.height = 600;

        // Khởi tạo các biến game
        this.balloon = {
            x: this.canvas.width / 2,
            y: this.canvas.height / 2,
            radius: 20,
            speedX: 3,
            speedY: 3,
            color: '#ff6b6b'
        };

        this.paddle = {
            x: this.canvas.width / 2 - 50,
            y: this.canvas.height - 20,
            width: 100,
            height: 10,
            color: '#4ecdc4',
            speed: 8
        };

        this.score = 0;
        this.gameOver = false;
        this.lastTime = Date.now();
        this.scoreInterval = 1000; // 1 giây
        this.lastScoreTime = Date.now();

        // Xử lý sự kiện bàn phím
        this.keys = {};
        window.addEventListener('keydown', (e) => {
            this.keys[e.key] = true;
        });

        window.addEventListener('keyup', (e) => {
            this.keys[e.key] = false;
        });

        // Bắt đầu game loop
        this.gameLoop();
    }

    update() {
        if (this.gameOver) return;

        // Di chuyển balloon
        this.balloon.x += this.balloon.speedX;
        this.balloon.y += this.balloon.speedY;

        // Kiểm tra va chạm với tường
        if (this.balloon.x - this.balloon.radius < 0 ||
            this.balloon.x + this.balloon.radius > this.canvas.width) {
            this.balloon.speedX = -this.balloon.speedX;
        }

        if (this.balloon.y - this.balloon.radius < 0) {
            this.balloon.speedY = -this.balloon.speedY;
        }

        // Kiểm tra va chạm với đáy (game over)
        if (this.balloon.y + this.balloon.radius > this.canvas.height) {
            this.gameOver = true;
            return;
        }

        // Kiểm tra va chạm với paddle
        if (this.balloon.y + this.balloon.radius > this.paddle.y &&
            this.balloon.x > this.paddle.x &&
            this.balloon.x < this.paddle.x + this.paddle.width) {
            this.balloon.speedY = -this.balloon.speedY;
            // Điều chỉnh hướng bóng dựa trên vị trí va chạm với paddle
            const hitPos = (this.balloon.x - (this.paddle.x + this.paddle.width / 2)) / (this.paddle.width / 2);
            this.balloon.speedX = hitPos * 5;
        }

        // Di chuyển paddle
        if (this.keys['ArrowLeft'] || this.keys['a']) {
            this.paddle.x -= this.paddle.speed;
            if (this.paddle.x < 0) this.paddle.x = 0;
        }

        if (this.keys['ArrowRight'] || this.keys['d']) {
            this.paddle.x += this.paddle.speed;
            if (this.paddle.x + this.paddle.width > this.canvas.width) {
                this.paddle.x = this.canvas.width - this.paddle.width;
            }
        }

        // Cập nhật điểm số mỗi giây
        const currentTime = Date.now();
        if (currentTime - this.lastScoreTime > this.scoreInterval) {
            this.score += 1;
            this.lastScoreTime = currentTime;
        }
    }

    draw() {
        // Xóa canvas
        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);

        // Vẽ balloon
        this.ctx.beginPath();
        this.ctx.arc(this.balloon.x, this.balloon.y, this.balloon.radius, 0, Math.PI * 2);
        this.ctx.fillStyle = this.balloon.color;
        this.ctx.fill();
        this.ctx.closePath();

        // Vẽ paddle
        this.ctx.beginPath();
        this.ctx.rect(this.paddle.x, this.paddle.y, this.paddle.width, this.paddle.height);
        this.ctx.fillStyle = this.paddle.color;
        this.ctx.fill();
        this.ctx.closePath();

        // Vẽ điểm số
        this.ctx.font = '20px Arial';
        this.ctx.fillStyle = '#333';
        this.ctx.fillText(`Điểm: ${this.score}`, 10, 30);

        // Hiển thị thông báo game over
        if (this.gameOver) {
            this.ctx.font = '40px Arial';
            this.ctx.fillStyle = '#ff0000';
            this.ctx.textAlign = 'center';
            this.ctx.fillText('GAME OVER', this.canvas.width / 2, this.canvas.height / 2);
            this.ctx.font = '20px Arial';
            this.ctx.fillText(`Điểm cuối cùng: ${this.score}`, this.canvas.width / 2, this.canvas.height / 2 + 50);
            this.ctx.textAlign = 'left';
        }
    }

    gameLoop() {
        this.update();
        this.draw();
        requestAnimationFrame(() => this.gameLoop());
    }
}

// Khởi tạo game khi trang được tải
new BalloonGame();