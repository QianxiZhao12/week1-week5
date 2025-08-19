import React, { useState, useEffect } from 'react';
import { Layout, Menu, Card, message } from 'antd';
import { BarChartOutlined, PieChartOutlined, LineChartOutlined } from '@ant-design/icons';
import ReactECharts from 'echarts-for-react';
import axios from 'axios';
import './App.css';

const { Header, Content, Sider } = Layout;

function App() {
  const [selectedMenu, setSelectedMenu] = useState('rating');
  const [chartData, setChartData] = useState(null);
  const [loading, setLoading] = useState(false);

  const menuItems = [
    {
      key: 'rating',
      icon: <BarChartOutlined />,
      label: '评分分布',
    },
    {
      key: 'year',
      icon: <LineChartOutlined />,
      label: '年份分布',
    },
    {
      key: 'country',
      icon: <PieChartOutlined />,
      label: '国家分布',
    },
  ];

  const fetchData = async (type) => {
    setLoading(true);
    try {
      const response = await axios.get(`/api/movies/${type}-distribution`);
      if (response.data.status === 'success') {
        setChartData(response.data.data);
      } else {
        message.error('获取数据失败');
      }
    } catch (error) {
      console.error('请求失败:', error);
      message.error('请求失败，请检查后端是否启动');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData(selectedMenu);
  }, [selectedMenu]);

  const getChartOption = () => {
    if (!chartData) return {};

    switch (selectedMenu) {
      case 'rating':
        return {
          title: {
            text: '豆瓣电影评分分布',
            left: 'center'
          },
          tooltip: {
            trigger: 'axis',
            axisPointer: {
              type: 'shadow'
            }
          },
          xAxis: {
            type: 'category',
            data: chartData.map(item => item.rating_range)
          },
          yAxis: {
            type: 'value',
            name: '电影数量'
          },
          series: [{
            data: chartData.map(item => item.count),
            type: 'bar',
            itemStyle: {
              color: '#1890ff'
            }
          }]
        };

      case 'year':
        return {
          title: {
            text: '豆瓣电影年代分布',
            left: 'center'
          },
          tooltip: {
            trigger: 'axis'
          },
          xAxis: {
            type: 'category',
            data: chartData.map(item => item.decade)
          },
          yAxis: {
            type: 'value',
            name: '电影数量'
          },
          series: [{
            data: chartData.map(item => item.count),
            type: 'line',
            smooth: true,
            itemStyle: {
              color: '#52c41a'
            }
          }]
        };

      case 'country':
        return {
          title: {
            text: '豆瓣电影国家分布',
            left: 'center'
          },
          tooltip: {
            trigger: 'item',
            formatter: '{a} <br/>{b}: {c} ({d}%)'
          },
          series: [{
            name: '电影数量',
            type: 'pie',
            radius: '50%',
            data: chartData.map(item => ({
              value: item.count,
              name: item.country_group
            })),
            emphasis: {
              itemStyle: {
                shadowBlur: 10,
                shadowOffsetX: 0,
                shadowColor: 'rgba(0, 0, 0, 0.5)'
              }
            }
          }]
        };

      default:
        return {};
    }
  };

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Header style={{ color: 'white', fontSize: '20px', textAlign: 'center' }}>
        豆瓣电影数据可视化
      </Header>
      <Layout>
        <Sider width={200} style={{ background: '#fff' }}>
          <Menu
            mode="inline"
            selectedKeys={[selectedMenu]}
            style={{ height: '100%', borderRight: 0 }}
            items={menuItems}
            onClick={({ key }) => setSelectedMenu(key)}
          />
        </Sider>
        <Layout style={{ padding: '24px' }}>
          <Content>
            <Card loading={loading}>
              <ReactECharts
                option={getChartOption()}
                style={{ height: '500px' }}
              />
            </Card>
          </Content>
        </Layout>
      </Layout>
    </Layout>
  );
}

export default App;