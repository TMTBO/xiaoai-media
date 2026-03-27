// 简单的调试脚本
console.log('=== 开始诊断 ===');

// 检查 Vue 导入
import { isRef } from 'vue';
console.log('✅ isRef 导入成功:', typeof isRef);

// 检查 API
import { api } from './src/api/index.ts';
console.log('✅ api 导入成功:', typeof api);

// 检查 composables
import { useDevices } from './src/composables/useDevices.ts';
console.log('✅ useDevices 导入成功:', typeof useDevices);

import { useGlobalState } from './src/composables/useGlobalState.ts';
console.log('✅ useGlobalState 导入成功:', typeof useGlobalState);

// 检查组件
import GlobalDeviceSelector from './src/components/GlobalDeviceSelector.vue';
console.log('✅ GlobalDeviceSelector 导入成功:', typeof GlobalDeviceSelector);

import GlobalPlayerBar from './src/components/GlobalPlayerBar.vue';
console.log('✅ GlobalPlayerBar 导入成功:', typeof GlobalPlayerBar);

console.log('=== 诊断完成 ===');
