// **********************************************************************
//
// Copyright (c) 2015 Red Hat, Inc. All rights reserved.
//
// **********************************************************************

#pragma once

module RemoteExecution {

	exception RequestCanceledException {
	};

	interface RemoteCommand {
		["ami", "amd"] idempotent string sendGridCommand(int jobid, out string other)
			throws RequestCanceledException;

		void shutdown();
	};
};
