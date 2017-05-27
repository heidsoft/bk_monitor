//全选
$('#table_demo3').find('.select-all').on('click', function(){
    if(this.checked){
        $('#table_demo3 :checkbox').prop('checked',true);
    }else{
        $('#table_demo3 :checkbox').prop('checked',false);
    }
});
$('#table_demo3').find(':checkbox').on('click', function(){
    if(!this.checked){
        $('#table_demo3').find('.select-all').prop('checked',false);
    }
}); 