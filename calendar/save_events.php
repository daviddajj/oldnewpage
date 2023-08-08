<?php
// 获取POST请求中的JSON数据
$data = file_get_contents('php://input');
$eventsData = json_decode($data);

if ($eventsData) {
  // 将JSON数据写入到 events.json 文件
  file_put_contents('events.json', json_encode($eventsData, JSON_PRETTY_PRINT));
  
  // 返回保存成功的响应
  $response = array('status' => 'success', 'message' => 'Events saved successfully.');
  echo json_encode($response);
} else {
  // 返回保存失败的响应
  $response = array('status' => 'error', 'message' => 'Failed to save events.');
  echo json_encode($response);
}
?>
