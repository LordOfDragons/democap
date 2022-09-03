# -*- coding: utf-8 -*-
#
# DEMoCap Blender Tools
#
# Copyright (C) 2022, DragonDreams (roland@dragondreams.ch)
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either
# version 2 of the License, or (at your option) any later
# version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.
#
# NOTE: For the GPL copy see http://www.gnu.org/licenses/gpl.html
#

import logging
import bpy
import sys
import asyncio
import concurrent.futures

from .utils import registerClass


logger = logging.getLogger(__name__)


def setup_asyncio_executor():
    """See https://github.com/lampysprites/blender-asyncio/blob/master/async_loop.py"""
    if sys.platform == 'win32':
        asyncio.get_event_loop().close()
        loop = asyncio.ProactorEventLoop()
        asyncio.set_event_loop(loop)
    else:
        loop = asyncio.get_event_loop()
    executor = concurrent.futures.ThreadPoolExecutor(max_workers=10)
    loop.set_default_executor(executor)


class AsyncLoopModalOperator(bpy.types.Operator):
    bl_idname = 'asyncio.loop'
    bl_label = 'Runs the asyncio main loop'

    _timer = None
    exit_loop = False

    def execute(self, context):
        return self.invoke(context, None)

    def invoke(self, context, event):
        logger.info("AsyncLoopModalOperator: Invoke")
        wm = context.window_manager
        wm.modal_handler_add(self)
        self.exit_loop = False
        self._timer = wm.event_timer_add(0.00001, window=context.window)
        return {'RUNNING_MODAL'}

    def modal(self, context, event):
        if self.exit_loop:
            logger.info("AsyncLoopModalOperator: Exit loop")
            context.window_manager.event_timer_remove(self._timer)
            self.exit_loop = False
            return {'FINISHED'}

        if event.type != 'TIMER':
            return {'PASS_THROUGH'}

        self.async_loop_once()
        return {'RUNNING_MODAL'}

    def async_loop_once(self):
        loop = asyncio.get_event_loop()
        if loop.is_closed():
            logger.warning('Async loop closed')
        else:
            loop.stop()
            loop.run_forever()


def startAsyncioLoop():
    logger.debug('Start async loop')
    return bpy.ops.asyncio.loop()


def stopAsyncioLoop():
    logger.debug('Stop async loop')
    AsyncLoopModalOperator.exit_loop = True
    loop = asyncio.get_event_loop()
    loop.stop()
    loop.run_forever()


def registerAsyncioOperator():
    setup_asyncio_executor()
    registerClass(AsyncLoopModalOperator)
