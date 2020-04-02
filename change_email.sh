git filter-branch --commit-filter '
        if [ "$GIT_AUTHOR_EMAIL" = "oldworkemail@company" ];
        then
                GIT_AUTHOR_NAME="Stef the Spineless";
                GIT_AUTHOR_EMAIL="stef@kotchan.org";
                git commit-tree "$@";
        else
                git commit-tree "$@";
        fi' HEAD
