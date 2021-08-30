function copyToClipboard(elementId) {
    console.log('function called')
    // 글을 쓸 수 있는 란을 만든다.
    let aux = document.createElement("input");
    // 지정된 요소의 값을 할당 한다.
    aux.setAttribute("value", document.getElementById(elementId).innerHTML);
    // body에 추가한다.
    document.body.appendChild(aux);
    // 지정된 내용을 강조한다.
    aux.select();
    // 텍스트를 카피하는 변수를 생성
    document.execCommand("copy");
    // body로 부터 다시 반환 한다.
    document.body.removeChild(aux);
}

function add_sample() {
    const div = document.createElement("div")

    div.classList.add("row")

    const input = document.createElement("div")
    const output = document.createElement("div")

    input.classList.add("col-6")
    output.classList.add("col-6")

    const input_label = document.createElement("label")
    const output_label = document.createElement("label")

    input_label.innerText = '예제 입력'
    output_label.innerText = '예제 출력'

    const input_textarea = document.createElement("textarea")
    const output_textarea = document.createElement("textarea")

    input_textarea.classList.add("form-control")
    input_textarea.setAttribute('name', `input`)
    output_textarea.classList.add("form-control")
    output_textarea.setAttribute('name', `output`)

    input.appendChild(input_label)
    input.appendChild(input_textarea)
    output.appendChild(output_label)
    output.appendChild(output_textarea)


    div.appendChild(input)
    div.appendChild(output)

    const form = document.querySelector('div.form-group#samples')
    form.appendChild(div)
}

function add_test_case() {
    // 나중에 예제와 테스트케이스를 직접 압축할 때 사용
    const div = document.createElement("div")

    div.classList.add("row")

    const test_case_file = document.createElement("div")
    const test_case_score = document.createElement("div")

    test_case_file.classList.add("col-6")
    test_case_score.classList.add("col-6")

    const test_case_file_label = document.createElement("label")
    const test_case_score_label = document.createElement("label")

    test_case_file_label.innerText = '테스트케이스 zip 파일'
    test_case_score_label.innerText = '테스트케이스 점수'

    const test_case_file_area = document.createElement("input")
    const test_case_score_area = document.createElement("input")

    test_case_file_area.type = 'file'
    test_case_file_area.classList.add("form-control")
    test_case_file_area.name = `test_case_file`

    test_case_score_area.type = 'number'
    test_case_score_area.classList.add("form-control")
    test_case_score_area.name = `test_case_score`
    test_case_score_area.defaultValue = 1
    test_case_score_area.min = 1
    test_case_score_area.max = 100

    test_case_file.appendChild(test_case_file_label)
    test_case_file.appendChild(test_case_file_area)
    test_case_score.appendChild(test_case_score_label)
    test_case_score.appendChild(test_case_score_area)

    div.appendChild(test_case_file)
    div.appendChild(test_case_score)

    const form = document.querySelector('div.form-group#test_case')
    form.appendChild(div)
}

function delete_modal() {
    let modal = document.getElementById("delete-modal")
    console.log("delete modal")
    if(modal.style.display === "none") modal.style.display = "flex"
    else modal.style.display = "none"
}