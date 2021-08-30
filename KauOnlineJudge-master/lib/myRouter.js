const flash = require('connect-flash')
const cookie = require('cookie-parser')
const express = require('express')
const passport = require('passport')
const requestIP = require('request-ip')
const bodyParser = require('body-parser')

passport.serializeUser((user, done) => {
    done(null, user)
})

passport.deserializeUser((user, done) => {
    done(null, user)
})

module.exports.Router = function() {
    const router = express.Router()

    //lib 폴더를 static으로 지정해 css, js, image 등을 사용할 수 있음
    router.use(express.static('lib'))
    
    //서드 파티 미들웨어
    router.use(bodyParser.urlencoded({ extended: false }))
    router.use(cookie())
    router.use(flash())
    router.use(passport.initialize())
    router.use(passport.session())

    //페이지를 만들 때 사용할 변수들
    router.build = {
        code: 200,
        page: '/',
        message: '',
        param: {
            title: 'KAU Online Judge'
        }
    }

    router.show = function (req, res) {
        var log = `[${new Date()}] ${req.method} ${req.originalUrl} ${req.user ? req.user.sessionid : requestIP.getClientIp(req)}\n${router.build.message}`
        //에러가 발생하지 않았다면 console에 log를, 발생했다면 error를 출력
        if (router.build.code < 400)   console.log(log)
        else                           console.error(log)

        //로그인 여부에 따라 param.user를 수정한다
        if (req.user) 
            router.build.param.user = req.user.username //req.session.username
        else router.build.param.user = undefined
    
        res.status(router.build.code).render(
            __dirname + '/../views/page/' + router.build.page, 
            router.build.param
        )
    }
    
    return router
}