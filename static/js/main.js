// 加载中状态函数
const isLoading = function isLoading(flag) {
    if (flag) {
        $(".mdui-progress").show();
        $("#result_dialog_buttom").hide();
    }
    else {
        $(".mdui-progress").hide();
        $("#result_dialog_buttom").show();
    }
};
// 校验MAC合法性
const checkMac = function isMacVaild(macValue) {
    if (macValue.length !== 17) {
        return false
    }
    let patten = new RegExp("^(([a-f0-9]{2}:)|([a-f0-9]{2}-)){5}[a-f0-9]{2}$", "ig");
    return patten.test(macValue)
};
const checkServer = function checkServer() {
    mdui.snackbar({
        message: '正在检查服务器',
        timeout: 100
    });
    $.ajax({
        type: "POST",
        url: "/api/send_package",
        timeout: 5000,
        data: {
            mac: '66-66-66-66-66-66',
            isp: '1',
            campus: '1'
        },
        success: function (msg) {
            if (msg === 'success'){
                mdui.snackbar({
                    message: '服务器正常',
                    timeout: 200
                });
            }
        }
    })
};
// jQuery函数
$(document).ready(function () {
    // 默认隐藏加载中进度条
    isLoading(false);
    // 测试服务器
    setTimeout((checkServer), 5000);
    // 按钮点击事件开始
    $("#btn").click(function () {
        // 先获取表单信息
        const macValue = $("#mac").val();
        const ispValue = $("#isp").val();
        const campusValue = $("#campus").val();
        console.log(macValue, ispValue, campusValue);
        // 校验用户输入合法性
        if (checkMac(macValue)) {
            // 弹出对话框，显示加载中状态
            $('#result_dialog .mdui-dialog-title').html('拼命加载中...');
            const inst = new mdui.Dialog('#result_dialog');
            inst.open();
            isLoading(true);

            // ajax请求开始
            $.ajax({
                type: "POST",
                url: "/api/send_package",
                timeout: 5000,
                data: {
                    mac: macValue,
                    isp: ispValue,
                    campus: campusValue
                },
                success: function (msg) {
                    isLoading(false);
                    if (msg === 'success') {
                        $('#result_dialog .mdui-dialog-title').html('预拨号成功，请查看拨号状态.');
                        mdui.snackbar({
                            message: '如果拨号失败请重启路由器'
                        });
                    }
                    if (msg === 'false') {
                        $('#result_dialog .mdui-dialog-title').html('服务器开小差了，正在抢救中...');
                    }
                    if (msg === 'error') {
                        $('#result_dialog .mdui-dialog-title').html('服务器BUG，医生说没救了...');
                    }
                },
                error: function (msg) {
                    isLoading(false);
                    $('#result_dialog .mdui-dialog-title').html('404 NotFound');
                }
            })
            // 结束ajax
        }
        else {
            mdui.snackbar({
                message: 'MAC地址格式错误.'
            });
            const inst = new mdui.Dialog('#failed_dialog');
            inst.open();
        }
    })
});
