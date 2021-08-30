const request = require('request')

const myRouter = require('../lib/myRouter')
const router = myRouter.Router()

router.get('/', (req, res) => {
    //로그인하지 않은 사용자가 접근할 경우 루트로 리다이렉트
    if (req.user == undefined) res.redirect('/')

    //router.show()를 사용하지 않으므로 콘솔에 로그를 띄운다
    console.log(`${new Date()} ${req.user.username}\nlogout`)

    //백엔드 서버에 로그아웃 요청을 보냄
    //에러를 받지 않음 -> 수정 필요
    request.get({
        uri: 'http://dofh.iptime.org:8000/api/logout/'//,
    })

    //passport.js에서 로그아웃을 진행한 뒤 임의의 주소로 리다이렉트
    req.logout()
    req.session.save((err) => {
        res.redirect('back')
    })
})

module.exports = router