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

/***********************************************************************************************************************
 * !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
 * THIS FILE IS AN AUTO-GENERATED FILE - DO NOT MODIFY IT.
 * !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
 **********************************************************************************************************************/

#include "mbed_toolchain.h" /* For using MBED_ALIGN macro */
#include "mbed_rtos_storage.h"
#include "spm_panic.h"
#include "spm_internal.h"
#include "psa_client_common.h"
#include "psa_{{partition.name|lower}}_partition.h"

/* Threads stacks */
MBED_ALIGN(8) uint8_t {{partition.name|lower}}_thread_stack[{{partition.stack_size}}] = {0};

/* Threads control blocks */
mbed_rtos_storage_thread_t {{partition.name|lower}}_thread_cb = {0};

/* Thread attributes - for thread initialization */
osThreadAttr_t {{partition.name|lower}}_thread_attr = {
    .name = "{{partition.name|lower}}",
    .attr_bits = 0,
    .cb_mem = &{{partition.name|lower}}_thread_cb,
    .cb_size = sizeof({{partition.name|lower}}_thread_cb),
    .stack_mem = {{partition.name|lower}}_thread_stack,
    .stack_size = {{partition.stack_size}},
    .priority = {{partition.priority}},
    .tz_module = 0,
    .reserved = 0
    };

secure_func_t {{partition.name|lower}}_sec_funcs[{{partition.name|upper}}_SF_COUNT] = {
{% for sf in partition.secure_functions %}
    {
        .sfid = {{sf.sfid|upper}},
        .mask = {{sf.signal|upper}},
        .partition = NULL,
        .min_version = {{sf.minor_version}},
        .min_version_policy = PSA_MINOR_VERSION_POLICY_{{sf.minor_policy|upper}},
{% if sf.nspe_callable %}
        .allow_nspe = true,
{% else %}
        .allow_nspe = false,
{% endif %}
    },
{% endfor %}
};

{% if partition.extern_sfids|count > 0 %}
/* External SFIDs used by {{partition.name}} */
const uint32_t {{partition.name|lower}}_external_sfids[{{partition.extern_sfids|count}}] =
{
{% for sfid in partition.extern_sfids %}
    {{sfid|upper}},
{% endfor %}
};
{% endif %}
{% for sf in partition.secure_functions %}
{% endfor %}

static mbed_rtos_storage_mutex_t {{partition.name|lower}}_mutex = {0};
static const osMutexAttr_t {{partition.name|lower}}_mutex_attr = {
    .name = "{{partition.name|lower}}_mutex",
    .attr_bits = osMutexRecursive | osMutexPrioInherit | osMutexRobust,
    .cb_mem = &{{partition.name|lower}}_mutex,
    .cb_size = sizeof(mbed_rtos_storage_mutex_t),
};

static mbed_rtos_storage_semaphore_t {{partition.name|lower}}_semaphore = {0};
static const osSemaphoreAttr_t {{partition.name|lower}}_sem_attr = {
    .name = "{{partition.name|lower}}_semaphore",
    .attr_bits = 0,
    .cb_mem = &{{partition.name|lower}}_semaphore,
    .cb_size = sizeof(mbed_rtos_storage_semaphore_t),
};

extern void {{partition.entry_point}}(void *ptr);

void {{partition.name|lower}}_init(partition_t *partition)
{
    if (NULL == partition) {
        SPM_PANIC("partition is NULL!\n");
    }

    partition->mutex = osMutexNew(&{{partition.name|lower}}_mutex_attr);
    if (NULL == partition->mutex) {
        SPM_PANIC("Failed to create mutex for secure partition {{partition.name|lower}}!\n");
    }

    partition->semaphore = osSemaphoreNew(
        PSA_SEC_FUNC_SEM_MAX_COUNT,
        PSA_SEC_FUNC_SEM_INITIAL_COUNT,
        &{{partition.name|lower}}_sem_attr
        );
    if (NULL == partition->semaphore) {
        SPM_PANIC("Failed to create semaphore for secure partition {{partition.name|lower}}!\n");
    }

    for (uint32_t i = 0; i < {{partition.name|upper}}_SF_COUNT; ++i) {
        {{partition.name|lower}}_sec_funcs[i].partition = partition;
    }
    partition->sec_funcs = {{partition.name|lower}}_sec_funcs;

    partition->thread_id = osThreadNew({{partition.entry_point}}, NULL, &{{partition.name|lower}}_thread_attr);
    if (NULL == partition->thread_id) {
        SPM_PANIC("Failed to create start main thread of partition {{partition.name|lower}}!\n");
    }
    partition->partition_state = PARTITION_STATE_IDLE;
}
{# End of file #}
