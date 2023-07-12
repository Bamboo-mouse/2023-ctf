function get_rank() {
  const req = new Request("https://homosserver.jp.eu.org:8080/");
  const pt = [1, 100, 150, 200, 300, 0];
  var ranking = [];
  let node;
  fetch(req).then((response) => {
    const data = response.json();
    let i = 0;
    for (let key in data) {
      let sum = 0;
      document.getElementById(key).remove();
      for (let j = 0; j < data[key].length; j++) {
        if (data[key][j]) {
          sum += pt[j];
        }
      }
      ranking[i] = [key, sum];
    }
    ranking.sort(function (a, b) {
      if (a[1] == b[1]) {
        return a[0] - b[0];
      }
      return b[1] - a[1];
    });
    ranking[0] = [ranking[0][0], ranking[0][1], 1];
    node = document.createElement("tr");
    node.id = ranking[0][0];
    node.innerHTML = `<td>${ranking[0][2]}</td><td>${ranking[0][0]}</td><td>${ranking[0][1]}</td>`;
    document.getElementById("scoreboard").appendChile(node);
    for (i = 1; i < ranking.length; i++) {
      ranking[i] = [
        ranking[i][0],
        ranking[i][1],
        ranking[i - 1][2] + (ranking[i][1] != ranking[i - 1][1]),
      ];
      node = document.createElement("tr");
      node.id = ranking[i][0];
      node.innerHTML = `<td>${ranking[i][2]}</td><td>${ranking[i][0]}</td><td>${ranking[i][1]}</td>`;
      document.getElementById("scoreboard").appendChild(node);
    }
  });
}
