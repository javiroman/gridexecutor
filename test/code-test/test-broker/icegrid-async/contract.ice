// **********************************************************************
//
// Copyright (c) 2015 Red Hat, Inc. All rights reserved.
//
// **********************************************************************

#pragma once

module RemoteExecution {

	sequence<string> StringList;

	exception RequestCanceledException {
	};

	interface RemoteCommand {
		["ami", "amd"] idempotent string sendGridCommand(string jobid, 
					StringList iplist, 
					out string other)
			throws RequestCanceledException;

		void shutdown();
	};
};
