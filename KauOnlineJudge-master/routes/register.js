const fs = require('fs')
const request = require('request')

const myRouter = require('../lib/myRouter')

const router = myRouter.Router()

function register_post (req, res) {
    //form에서 받아온 정보의 집합
    var post = req.body

    if (post.password != post.password_check) {
        //비밀번호와 비밀번호 확인이 일치하지 않는다면
        //경고창을 표시한 뒤 다시 회원가입 페이지로 이동
        req.flash('error', 'password:\n    Password not matched!')
        console.log('password != password_check')
        
        req.session.save(() => {
            res.redirect('/register')
        })
    
        return false
    } else if (post.agree != 'on') {
        //이용약관에 동의하지 않는다면
        //경고창을 표시한 뒤 다시 회원가입 페이지로 이동
        req.flash('error', 'Please Agree to the Terms of Use!')
        console.log('terms of use unchecked')
        
        req.session.save(() => {
            res.redirect('/register')
        })
    
        return false
    }

    //request로 전송할 데이터 집합
    const register = {
        url: 'http://dofh.iptime.org:8000/api/register/',
        form: { 
            username: post.username,
            email: post.email,
            password: post.password
        }
    }

    request.post(register, (err, serverRes, body) => {
        if (err) {     //회원가입 요청에 실패한 경우 
            req.flash('error', 'Unknown Server Error!')
            console.error(err)
            
            req.session.save(() => {
                res.redirect('/register')
            })
        }    //회원가입 요청에 실패한 경우 

        //body는 json 형태의 파일이므로 이를 해석 가능하게끔 파싱
        body = JSON.parse(body)

        if (body.error) {   //백엔드에서 회원가입을 거부했다면
            //거부 사유가 담긴 body.data를 string화 한 뒤 에러메세지로 띄운다
            let message = ''
            for (item in body.data) {
                if (item != 'non_field_errors')
                    message += item + ':\n'
                body.data[item].forEach(msg => {
                    message += '    ' + msg + '\n'
                })
            }

            req.flash('error', message)

            req.session.save(() => {
                res.redirect('/register')
            })
        } else {
            //회원가입 메세지를 띄운 뒤 로그인 페이지로 리다이렉트
            req.flash('error', 'You have successfully registered!\nNow you can log in.')
            console.log(`${post.username} registered`)
            
            req.session.save(() => {
                res.redirect('/login')
            })
        }
    }) 
}

router.get('/', (req, res) => {    //회원가입 페이지
    router.build = {
        code: 200,
        page: 'register',
        message: 'register',
        param: {
            title: 'Register',
            flash: req.flash()
        }
    }

    //각 페이지에 해당하는 내용을 완성했으면 log와 함께 페이지를 표시한다
    router.show(req, res)
})

router.post('/', register_post)

module.exports = router
/* */