/* Copyright (c) 2017 ARM Limited
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

#include "mbed_error.h"
#include "mbed_rtos_storage.h"
#include "spm_internal.h"
#include "handles_manager.h"

psa_handle_item_t g_channels_handle_storage[MBED_CONF_SPM_IPC_MAX_NUM_OF_CHANNELS] = {0};
extern psa_handle_item_t g_messages_handle_storage[];


mbed_rtos_storage_mem_pool_t g_channel_mem_pool_storage = {0};
ipc_channel_t g_channel_data[MBED_CONF_SPM_IPC_MAX_NUM_OF_CHANNELS] = {0};
osMemoryPoolAttr_t g_channel_mem_pool_attr = {
    .name = "SPM_channel_pool",
    .attr_bits = 0,
    .cb_mem = &g_channel_mem_pool_storage,
    .cb_size = sizeof(g_channel_mem_pool_storage),
    .mp_mem = g_channel_data,
    .mp_size = sizeof(g_channel_data)
};

spm_t g_spm = {0};

// forward declaration
uint32_t init_partitions(partition_t **partitions);

void psa_spm_init(void)
{
    psa_hndl_mgr_init(&(g_spm.channels_handle_mgr), g_channels_handle_storage, MBED_CONF_SPM_IPC_MAX_NUM_OF_CHANNELS);

    g_spm.channel_mem_pool = osMemoryPoolNew(
        MBED_CONF_SPM_IPC_MAX_NUM_OF_CHANNELS,
        sizeof(ipc_channel_t),
        &g_channel_mem_pool_attr
        );
    if (NULL == g_spm.channel_mem_pool) {
        error("%s - Failed to create channel memory pool!\n", __func__);
    }

    g_spm.partition_count = init_partitions(&(g_spm.partitions));

    if (g_spm.partition_count > 0) {
        psa_hndl_mgr_init(&(g_spm.messages_handle_mgr), g_messages_handle_storage, g_spm.partition_count);
    }
}
