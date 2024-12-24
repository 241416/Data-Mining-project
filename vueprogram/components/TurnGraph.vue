<template>
  <div>
    <ul>
      <!-- 每个按钮绑定不同的文件名 -->
      <li><button @click="loadGraph('arctic_0.gexf')"><h3>11月06日</h3></button></li>
      <li><button @click="loadGraph('arctic_1.gexf')"><h3>11月07日</h3></button></li>
      <li><button @click="loadGraph('arctic_2.gexf')"><h3>11月08日</h3></button></li>
      <li><button @click="loadGraph('arctic_3.gexf')"><h3>11月09日</h3></button></li>
      <li><button @click="loadGraph('arctic_4.gexf')"><h3>11月10日</h3></button></li>
      <li><button @click="loadGraph('desert_5.gexf')"><h3>11月11日</h3></button></li>
      <li><button @click="loadGraph('arctic_6.gexf')"><h3>11月12日</h3></button></li>
      <li><button @click="loadGraph('arctic_7.gexf')"><h3>11月13日</h3></button></li>
      <li><button @click="loadGraph('arctic_8.gexf')"><h3>11月14日</h3></button></li>
      <li><button @click="loadGraph('arctic_9.gexf')"><h3>11月15日</h3></button></li>
    </ul>
    <div id="graph-container"></div>
  </div>
</template>

<script>
import Graph from "graphology";
import { parse } from "graphology-gexf/browser";
import Sigma from "sigma";

export default {
  name: "TurnGraph",
  data() {
    return {
      renderer: null,
    };
  },
  methods:{
    showNodeLabel(container, label) {
    this.hideNodeLabel(container); // 确保清除旧标签

    const labelDiv = document.createElement("div");
    labelDiv.id = "hovered-node-label";
    labelDiv.className = "node-label";
    labelDiv.textContent = label;

    labelDiv.style.position = "absolute";
    labelDiv.style.left = `20px`;
    labelDiv.style.top = `20px`;
    labelDiv.style.backgroundColor = "rgba(255, 255, 255, 0.8)";
    labelDiv.style.border = "1px solid #ccc";
    labelDiv.style.borderRadius = "5px";
    labelDiv.style.padding = "5px 10px";
    labelDiv.style.pointerEvents = "none";
    labelDiv.style.maxWidth = "400px";
    labelDiv.style.wordWrap = "break-word";
    labelDiv.style.whiteSpace = "normal";

    container.appendChild(labelDiv);
  },

  loadGraph(fileName) {
    fetch(`./${fileName}`)
      .then((res) => {
        if (!res.ok) throw new Error(`Failed to load file: ${fileName}`);
        return res.text();
      })
      .then((gexf) => {
        if (!this.isValidGEXF(gexf)) {
          alert("Invalid GEXF file format.");
          return;
        }

          try {
            const graph = parse(Graph, gexf);

            const container = document.getElementById("graph-container");
            if (this.renderer) this.renderer.kill();

            if (container) {
              this.renderer = new Sigma(graph, container, {
                renderLabel: (node, context) => {
                const group = graph.getNodeAttribute(node, "content");
                if (group === 1) return null;
                const label = graph.getNodeAttribute(node, "label");
                context.fillText(label, 0, 0);
              },
              minCameraRatio: 0.08,
              maxCameraRatio: 3,
              });
              // this.renderer = new Sigma(graph, container, {
              //   renderLabel: () => null, 
              //   minCameraRatio: 0.08,
              //   maxCameraRatio: 3,
              //   settings: {
              //   drawLabels: false, // 禁用标签绘制
              //   labelDensity: 0, // 标签密度为 0
              //   labelSize: 0, // 标签大小为 0
              //   defaultLabelColor: "none", // 默认标签颜色设为空
              // },
              // });

             

              // 修复 Sigma 渲染层样式
              const canvasElements = container.querySelectorAll("canvas.sigma-mouse");
              canvasElements.forEach((canvas) => {
                canvas.style.position = "relative";
                canvas.style.width = "100%";
                canvas.style.height = "100%";
              });

              // 节点悬停事件
              this.renderer.on("enterNode", ({ node }) => {
              const nodeAttributes = graph.getNodeAttributes(node);
              const nodeData = this.renderer.getNodeDisplayData(node);

              const content = graph.getNodeAttribute(node, "content");
              const labelToDisplay = content || nodeAttributes.label || "Unnamed Node";

              this.showNodeLabel(container, labelToDisplay, nodeData);
  
            });

            // 隐藏标签
            this.renderer.on("leaveNode", () => {
              this.hideNodeLabel(container);
            });
              // this.renderer.on("enterNode", ({ node }) => {
              //   const nodeAttributes = graph.getNodeAttributes(node);
              //   const nodeData = this.renderer.getNodeDisplayData(node);
              //   this.showNodeLabel(container, nodeAttributes.label, nodeData);
              // });
            }

                  
          } catch (error) {
            console.error("Error parsing GEXF file:", error);
            alert("Failed to parse GEXF file. Please check the file format.");
          }
        })
        .catch((error) => {
          console.error("Error loading GEXF file:", error);
          alert("An error occurred while loading the file.");
        });
    },

  
    
    // 隐藏节点标签
    hideNodeLabel(container) {
      const existingLabel = container.querySelector("#hovered-node-label");
      if (existingLabel) container.removeChild(existingLabel);
    },

    
    // 验证 GEXF 文件格式
    isValidGEXF(gexf) {
      const gexfPattern = /<gexf[\s\S]+<\/gexf>/;
      return gexfPattern.test(gexf);
    },

    // 拆分长标签为多行
    breakLabelIntoLines(label, maxLineLength) {
      return label.match(new RegExp(`.{1,${maxLineLength}}`, "g")).join("\n");
    },
  },

  mounted() {
    this.loadGraph("arctic_0.gexf");
  },

  unmounted() {
    if (this.renderer) {
      this.renderer.kill();
      this.renderer = null;
    }
  },
};
</script>

<style scoped>
button {
  background-color: #d1e5ff;
  border-radius: 10px;
  border: 0;
  border-left: 1rem solid #4091fc;
  transition: transform 0.3s ease, background-color 0.3s ease;
}

button:hover {
  transform: scale(1.1);
  background-color: #b0d4ff;
}

ul {
  list-style-type: none;
  padding: 0;
}

li {
  display: inline-block;
  margin: 0 50px 20px 0;
}

#graph-container {
  width: 100%;
  height: 85vh;
  position: relative;
}

.node-label {
  font-size: 12px;
  text-align: center;
}
</style>
