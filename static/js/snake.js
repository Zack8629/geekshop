"use strict";

const settings = {
    rowsCount: 15,
    colsCount: 15,
    speed: 2,
    winFoodCount: 30,
};

const config = {
    settings,

    init(userSettings) {
        Object.assign(this.settings, userSettings);
    },

    getRowsCount() {
        return this.settings.rowsCount;
    },

    getColsCount() {
        return this.settings.colsCount;
    },

    getSpeed() {
        return this.settings.speed;
    },

    getWinFoodCount() {
        return this.settings.winFoodCount;
    },

    validate() {
        const result = {
            isValid: true,
            errors: [],
        };

        if (this.settings.rowsCount < 10 || this.settings.rowsCount > 30) {
            result.isValid = false;
            result.errors.push('Неверные настройки, значение rowsCount должно быть в диапазоне [10, 30].');
        }

        if (this.settings.colsCount < 10 || this.settings.colsCount > 30) {
            result.isValid = false;
            result.errors.push('Неверные настройки, значение colsCount должно быть в диапазоне [10, 30].');
        }

        if (this.settings.speed < 1 || this.settings.speed > 10) {
            result.isValid = false;
            result.errors.push('Неверные настройки, значение speed должно быть в диапазоне [1, 10].');
        }

        if (this.settings.winFoodCount < 5 || this.settings.winFoodCount > 60) {
            result.isValid = false;
            result.errors.push('Неверные настройки, значение winLength должно быть в диапазоне [5, 60].');
        }

        return result;
    },
};

const map = {
    cells: null,
    usedCells: null,

    init(rowsCount, colsCount) {
        const table = document.getElementById('game');
        table.innerHTML = "";
        this.cells = {};
        this.usedCells = [];
        for (let row = 0; row < rowsCount; row++) {
            const tr = document.createElement('tr');
            tr.classList.add('row');
            table.appendChild(tr);
            for (let col = 0; col < colsCount; col++) {
                const td = document.createElement('td');
                td.classList.add('cell');
                this.cells[`x${col.toString()}_y${row.toString()}`] = td;
                tr.appendChild(td);
            }
        }
    },

    render(snakePointsArray, foodPoint, barrierPoint) {
        for (const cell of this.usedCells) {
            cell.className = 'cell';
        }
        this.usedCells = [];

        snakePointsArray.forEach((point, idx) => {
            const snakeCell = this.cells[`x${point.x}_y${point.y}`];
            snakeCell.classList.add(idx === 0 ? 'snakeHead' : 'snakeBody');
            this.usedCells.push(snakeCell);
        });

        const foodCell = this.cells[`x${foodPoint.x}_y${foodPoint.y}`];
        foodCell.classList.add('food');
        this.usedCells.push(foodCell);

        const barrierCell = this.cells[`x${barrierPoint.x}_y${barrierPoint.y}`];
        barrierCell.classList.add('barrier');
        this.usedCells.push(barrierCell);

    },
};

const snake = {
    body: null,
    direction: null,
    lastStepDirection: null,
    maxX: null,
    maxY: null,

    init(startBody, direction, maxX, maxY) {
        this.body = startBody;
        this.direction = direction;
        this.lastStepDirection = direction;
        this.maxX = maxX;
        this.maxY = maxY;
    },

    getBody() {
        return this.body;
    },

    getLastStepDirection() {
        return this.lastStepDirection;
    },

    isOnPoint(point) {
        return this.body.some(snakePoint => snakePoint.x === point.x && snakePoint.y === point.y);
    },

    makeStep() {
        this.lastStepDirection = this.direction;
        this.body.unshift(this.getNextStepHeadPoint());
        this.body.pop();
    },

    growUp() {
        const lastBodyIdx = this.body.length - 1;
        const lastBodyPoint = this.body[lastBodyIdx];
        const lastBodyPointClone = Object.assign({}, lastBodyPoint);
        this.body.push(lastBodyPointClone);
    },

    getNextStepHeadPoint() {
        const firstPoint = this.body[0];
        switch (this.direction) {
            case 'up':
                return { x: firstPoint.x, y: firstPoint.y !== 0 ? firstPoint.y - 1 : this.maxY };
            case 'right':
                return { x: firstPoint.x !== this.maxX ? firstPoint.x + 1 : 0, y: firstPoint.y };
            case 'down':
                return { x: firstPoint.x, y: firstPoint.y !== this.maxY ? firstPoint.y + 1 : 0 };
            case 'left':
                return { x: firstPoint.x !== 0 ? firstPoint.x - 1 : this.maxX, y: firstPoint.y };
        }
    },

    setDirection(direction) {
        this.direction = direction;
    },
};

const food = {
    x: null,
    y: null,

    getCoordinates() {
        return {
            x: this.x,
            y: this.y,
        }
    },

    setCoordinates(point) {
        this.x = point.x;
        this.y = point.y;
    },

    isOnPoint(point) {
        return this.x === point.x && this.y === point.y;
    },
};

const barrier = {
    x: null,
    y: null,

    getCoordinates() {
        return {
            x: this.x,
            y: this.y,
        }
    },

    setCoordinates(point) {
        this.x = point.x;
        this.y = point.y;
    },

    isOnPoint(point) {
        return this.x === point.x && this.y === point.y;
    },
};

const status = {
    condition: null,

    setPlaying() {
        this.condition = 'playing';
    },

    setStopped() {
        this.condition = 'stopped';
    },

    setFinished() {
        this.condition = 'finished';
    },

    isPlaying() {
        return this.condition === 'playing';
    },

    isStopped() {
        return this.condition === 'stopped';
    },
};

const score = {
    count: null,
    countEl: null,

    init() {
        this.countEl = document.getElementById('score-count');
        this.drop();
    },

    increment() {
        this.count++;
        this.render();
    },

    drop() {
        this.count = 0;
        this.render();
    },

    render() {
        this.countEl.textContent = this.count;
    }
};

const game = {
    config,
    map,
    snake,
    food,
    barrier,
    status,
    score,
    tickInterval: null,

    init(userSettings) {
        this.config.init(userSettings);
        const validation = this.config.validate();

        if (!validation.isValid) {
            for (const err of validation.errors) {
                console.error(err);
            }
            return;
        }
        this.map.init(this.config.getRowsCount(), this.config.getColsCount());
        this.score.init();
        this.setEventHandlers();
        this.reset();
    },

    reset() {
        this.stop();
        this.score.drop();
        this.snake.init(this.getStartSnakeBody(), 'up', this.config.getColsCount() - 1, this.config.getRowsCount() - 1);
        this.food.setCoordinates(this.getRandomFreeCoordinates());
        this.Setbarrier();
        this.render();
    },

    play() {
        this.status.setPlaying();
        this.tickInterval = setInterval(() => this.tickHandler(), 1000 / this.config.getSpeed());
        this.setPlayButton('Пауза');
    },

    stop() {
        this.status.setStopped();
        clearInterval(this.tickInterval);
        this.setPlayButton('Старт');
    },

    finish() {
        this.status.setFinished();
        clearInterval(this.tickInterval);
        this.setPlayButton('Игра закончена', true);
    },

    tickHandler() {
        if (!this.canMakeStep()) {
            return this.finish();
        };

        // if (score.count % 2 === 0 && score.count !== -1) {
        //     this.Setbarrier();
        // }

        if (this.barrier.isOnPoint(this.snake.getNextStepHeadPoint())) {
            return this.finish();
        };

        if (this.food.isOnPoint(this.snake.getNextStepHeadPoint())) {
            this.snake.growUp();
            this.score.increment();
            this.food.setCoordinates(this.getRandomFreeCoordinates());
            if (this.isGameWon()) {
                this.finish();
            }
        }

        this.snake.makeStep();
        this.render();
    },

    Setbarrier() {
        this.barrier.setCoordinates(this.getRandomFreeCoordinates());
    },

    setPlayButton(textContent, isDisabled = false) {
        const playButton = document.getElementById('playButton');
        playButton.textContent = textContent;
        isDisabled ? playButton.classList.add('disabled') : playButton.classList.remove('disabled');
    },

    getStartSnakeBody() {
        return [{
            x: Math.floor(this.config.getColsCount() / 2),
            y: Math.floor(this.config.getRowsCount() / 2)
        }];
    },

    setEventHandlers() {
        document.getElementById('playButton').addEventListener('click', () => this.playClickHandler());
        document.getElementById('newGameButton').addEventListener('click', event => this.newGameClickHandler(event));
        document.addEventListener('keydown', event => this.keyDownHandler(event));
    },

    render() {
        this.map.render(this.snake.getBody(), this.food.getCoordinates(), this.barrier.getCoordinates());
    },

    getRandomFreeCoordinates() {
        const exclude = [this.food.getCoordinates(), this.barrier.getCoordinates(), ...this.snake.getBody()];

        while (true) {
            const rndPoint = {
                x: Math.floor(Math.random() * this.config.getColsCount()),
                y: Math.floor(Math.random() * this.config.getRowsCount()),
            };

            if (!exclude.some(exPoint => rndPoint.x === exPoint.x && rndPoint.y === exPoint.y)) {
                return rndPoint;
            }
        }
    },

    playClickHandler() {
        if (this.status.isPlaying()) {
            this.stop();
        } else if (this.status.isStopped()) {
            this.play();
        }
    },

    newGameClickHandler() {
        this.reset();
    },

    keyDownHandler(event) {
        if (!this.status.isPlaying()) {
            return;
        }
        const direction = this.getDirectionByCode(event.code);

        if (this.canSetDirection(direction)) {
            this.snake.setDirection(direction);
        }
    },

    getDirectionByCode(code) {
        switch (code) {
            case 'KeyW':
            case 'ArrowUp':
                return 'up';
            case 'KeyD':
            case 'ArrowRight':
                return 'right';
            case 'KeyS':
            case 'ArrowDown':
                return 'down';
            case 'KeyA':
            case 'ArrowLeft':
                return 'left';
            default:
                return '';
        }
    },

    canSetDirection(direction) {
        const lastStepDirection = this.snake.getLastStepDirection();

        return direction === 'up' && lastStepDirection !== 'down' ||
            direction === 'right' && lastStepDirection !== 'left' ||
            direction === 'down' && lastStepDirection !== 'up' ||
            direction === 'left' && lastStepDirection !== 'right';
    },

    isGameWon() {
        return this.snake.getBody().length > this.config.getWinFoodCount();
    },

    canMakeStep() {
        return !this.snake.isOnPoint(this.snake.getNextStepHeadPoint());
    },
};

game.init({ rowsCount: 20, colsCount: 20, speed: 6, winFoodCount: 40 });


