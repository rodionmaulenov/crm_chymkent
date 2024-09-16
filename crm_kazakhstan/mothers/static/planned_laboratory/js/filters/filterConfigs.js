const filterConfigs = {
    timeToVisit: {
        correctOrder: ['new_visit', 'visit', 'not_visit'],
        url: '/admin/mothers/plannedlaboratory/get_filter_choices/',
        filterHeadingText: 'By time to visit',
        paramName: 'time_new_visit'
    },
    usersObjects: {
        correctOrder: [],  // You can leave this empty if there's no specific order
        url: '/admin/mothers/plannedlaboratory/get_users_objects_choices/', // Update with the correct URL
        filterHeadingText: 'Users Objects',
        paramName: 'username'
    }
};

