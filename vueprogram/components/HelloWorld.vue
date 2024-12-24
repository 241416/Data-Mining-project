<template>
  <div class="hello">
    <div class="header-container">
    <br>
    <h1>{{ msg }}</h1>
   <button> <a href="https://shaoshixuan.github.io/shaoshixuan.gitub.io/dataview/Data-Mining-project/index"><p>跳转</p></a></button>
  </div></div>
</template>

<script>
export default {
  name: 'HelloWorld',
  props: {
    msg: String
  }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
a
{
  text-decoration:none;
  color:#000;
}
h1 {
  margin: 0;
}

button {
  background-color: #d1e5ff;
  border-radius: 10px;
  border:0;
  border-left: 1rem solid #4091fc;
  transition: transform 0.3s ease, background-color 0.3s ease; /* 添加过渡效果 */
}

button:hover {
  transform: scale(1.1); /* 鼠标悬停时放大 */
  background-color: #b0d4ff; /* 鼠标悬停时变色 */
}

.header-container {
  display: flex; /* 使用 Flexbox 布局 */
  align-items: center; /* 垂直方向居中 */
}


button {
  margin-left: auto; /* 将按钮推到最右侧 */
}

.node-label {
  white-space: normal; /* 允许文本换行 */
  word-wrap: break-word; /* 如果单词太长，会在单词之间换行 */
  overflow-wrap: break-word; /* 确保长文本也会换行 */
  max-width: 150px; /* 可选：根据需要调整最大宽度 */
  word-break: break-all; /* 如果必要，强制单词中断并换行 */
}
</style>
