const fs = require('fs')
const request = require('request')
const passport = require('passport')
const LocalStrategy = require('passport-local').Strategy

const myRouter = require('../lib/myRouter')

const router = myRouter.Router()

passport.use(new LocalStrategy(
    // {
    //     usernameField: 'username',
    //     passwordField: 'password'
    // }
    login_post
))


function login_post (username, password, done) {
    //request로 전송할 데이터 집합
    const login = {
        uri: 'http://dofh.iptime.org:8000/api/login/',
        form: {
            username: username,
            email: username,
            password: password
        }
    }

    //request를 이용해 로그인 정보를 백엔드에 전송
    request.post(login, function (err, serverRes, body) {
        if (err) {                  //로그인 요청에 실패한 경우 
            console.error(err)
            return done(null, false, { message: 'unknown Error!' })
        }

        //body는 json 형태의 파일이므로 이를 해석 가능하게끔 파싱
        body = JSON.parse(body)

        if (body.error != null) {   //로그인에 실패한 경우
            //에러메세지를 표시한 뒤 이전 페이지로 이동해야 함
            return done(null, false, { message: 'Username or Password Incorrect!' })
        } 

        let res_cookie = [
            serverRes.headers['set-cookie'][0].split('; '),
            serverRes.headers['set-cookie'][1].split('; ')
        ]
        login.form.csrftoken = res_cookie[0][0].split('=')[1]
        login.form.sessionid = res_cookie[1][0].split('=')[1]
        
        //정상적으로 로그인을 실행
        return done(null, login.form)
    })
}

router.get('/', (req, res) => {    //로그인 페이지
    //이전 페이지가 로그인 후 리다이렉트 할 수 있는 페이지가 아니라면
    if (!['login', 'register'].includes(req.headers.referer.split('/')[3])) {
        //이전 페이지가 지정해 준 리다이렉트, 혹은 이전 페이지로 리다이렉트를 설정한다
        router.redirect = (req.session.redirect) ? req.session.redirect : req.headers.referer
    }

    router.build = {
        code: 200,
        page: 'login',
        message: 'login',
        param: {
            title: 'Login',
            flash: req.flash()
        }
    }

    //각 페이지에 해당하는 내용을 완성했으면 log와 함께 페이지를 표시
    router.show(req, res)
})

router.post('/',                        //passport로 로그인한 뒤 미리 지정한 경로로 리다이렉트
    passport.authenticate('local', {
        failureRedirect: '/login',
        failureFlash: true
    }),
    (req, res) => {
        //세션을 저장하지 않으면 로그인 반영이 늦어짐
        req.session.save(() => {
            //이전에 설정한 리다이렉트를 제거한 뒤 리다이렉트
            res.redirect((router.redirect != undefined) ? router.redirect : '/')
        })
    }
)

module.exports = router