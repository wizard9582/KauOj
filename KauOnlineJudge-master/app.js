const express = require('express')
const session = require('express-session')
const FileStore = require('session-file-store')(session)

const app = express()

//pug
app.set('view engine', 'pug')
app.set('views', './views')


//페이지에서 사용할 세션의 정보
app.use(session({
    //secure: true,
    HttpOnly: true,
    secret: 'KAUOnlineJudge',
    resave: false,
    saveUninitialized: false,
    store: new FileStore()
}))

//routes 폴더 안의 가나다 순으로 정렬해야 하는 것으로 보임
app.use('/login',       require('./routes/login'))    //로그인 페이지
app.use('/logout',      require('./routes/logout'))   //로그아웃 페이지
app.use('/question',    require('./routes/question')) /*문제 페이지, 문제정보 열람 불가?*/
app.use('/register',    require('./routes/register')) //회원가입 페이지
app.use('/',            require('./routes/root'))     //기본 페이지
app.use('/user',        require('./routes/user'))     //사용자 정보 페이지

app.listen(8080, function() {})